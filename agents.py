import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AgentGroupChat, AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.agents.strategies import TerminationStrategy, SequentialSelectionStrategy
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions.kernel_function_decorator import kernel_function

# Agent Names
GENERAL = "GeneralAgent"
CALL_CENTER = "CallCenterAgent"
TRANSLATION = "TranslationAgent"
DOCUMENT = "DocumentAgent"
FABRIC = "FabricDataAgent"
POWERBI = "PowerBIReportingAgent"
PMO = "PMOAgent"

# Agent Instructions
GENERAL_INSTRUCTIONS = "Handle general inquiries about application status, service info, or other citizen requests not related to translation or documents."

CALL_CENTER_INSTRUCTIONS = """
You are the first point of contact for citizens. 
Identify if the query is a document, a translation request, or a general question.
Return the name of the agent to route to: DocumentAgent, TranslationAgent, or General.
Do not ask follow-up questions. Just return the route.
"""

TRANSLATION_INSTRUCTIONS = "Translate between Arabic and English. Maintain context and accuracy."
DOCUMENT_INSTRUCTIONS = "Extract structured data from documents (PDFs, images, forms)."
FABRIC_INSTRUCTIONS = "Store structured data and prepare it for analysis."
POWERBI_INSTRUCTIONS = "Generate dashboards and reports from Fabric data."
PMO_INSTRUCTIONS = "Log all interactions and trigger workflows. Maintain audit trails."

# Plugins
class GeneralPlugin:
    @kernel_function(description="Handles general citizen queries")
    def handle_general_query(self, query: str = "") -> str:
        # Customize logic as needed
        if "status" in query.lower():
            return "You can find your application status on the citizen portal or by contacting support."
        return "Thank you for your inquiry. We will get back to you soon."

class CallCenterPlugin:
    @kernel_function(description="Routes citizen queries to appropriate agents")
    def route_query(self, query: str = "") -> str:
        if "document" in query.lower():
            return "DocumentAgent"
        elif "arabic" in query.lower() or "translate" in query.lower():
            return "TranslationAgent"
        return "General"

class TranslationPlugin:
    @kernel_function(description="Translates text between Arabic and English")
    def translate_text(self, text: str = "") -> str:
        return f"Translated: {text}"

class DocumentPlugin:
    @kernel_function(description="Extracts structured data from documents")
    def extract_document_data(self, document: str = "") -> dict:
        return {"name": "John Doe", "id": "12345", "doc_type": "Form"}

class FabricPlugin:
    @kernel_function(description="Stores structured data for analysis")
    def store_to_fabric(self, data: dict = {}) -> str:
        return "Data stored in Fabric"

class PowerBIPlugin:
    @kernel_function(description="Generates Power BI reports")
    def generate_report(self, data: dict = {}) -> str:
        return "Power BI Dashboard URL"


class PMOPlugin:
    @kernel_function(description="Logs interaction and triggers workflows")
    def log_interaction(self, session: str = "") -> str:
        return "Interaction logged and workflow triggered"


# Selection Strategy
class ContactCenterSelectionStrategy(SequentialSelectionStrategy):
    async def select_agent(self, agents, history):
        if not history:
            return next((a for a in agents if a.name == CALL_CENTER), None)

        last = history[-1]
        if last.role == AuthorRole.USER:
            return next((a for a in agents if a.name == CALL_CENTER), None)
        elif getattr(last, 'name', None) == CALL_CENTER:
            route = last.content.strip()
            return next((a for a in agents if a.name == route), None)
        elif getattr(last, 'name', None) in [DOCUMENT, TRANSLATION]:
            return next((a for a in agents if a.name == FABRIC), None)
        elif getattr(last, 'name', None) == FABRIC:
            return next((a for a in agents if a.name == POWERBI), None)
        elif getattr(last, 'name', None) == POWERBI:
            return next((a for a in agents if a.name == PMO), None)
        elif getattr(last, 'name', None) == PMO:
            return None  # Stop here
        elif getattr(last, 'name', None) == GENERAL:
            return None  # General agent handles the last step
        return None




# Termination Strategy
class ContactCenterTerminationStrategy(TerminationStrategy):
    async def should_agent_terminate(self, agent, history):
        return any("Interaction logged" in msg.content for msg in history if msg.role == AuthorRole.ASSISTANT)

# Main
async def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    ai_agent_settings = AzureAIAgentSettings()

    async with (
        DefaultAzureCredential(exclude_environment_credential=True, exclude_managed_identity_credential=True) as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ):
        agent_defs = [
            (CALL_CENTER, CALL_CENTER_INSTRUCTIONS, [CallCenterPlugin()]),
            (TRANSLATION, TRANSLATION_INSTRUCTIONS, [TranslationPlugin()]),
            (DOCUMENT, DOCUMENT_INSTRUCTIONS, [DocumentPlugin()]),
            (FABRIC, FABRIC_INSTRUCTIONS, [FabricPlugin()]),
            (POWERBI, POWERBI_INSTRUCTIONS, [PowerBIPlugin()]),
            (PMO, PMO_INSTRUCTIONS, [PMOPlugin()]),
            (GENERAL, GENERAL_INSTRUCTIONS, [GeneralPlugin()]),  
        ]


        agents = []
        for name, instructions, plugins in agent_defs:
            definition = await client.agents.create_agent(
                model=ai_agent_settings.model_deployment_name,
                name=name,
                instructions=instructions
            )
            agents.append(AzureAIAgent(client=client, definition=definition, plugins=plugins))

        # Orchestrate group chat
        chat = AgentGroupChat(
            agents=agents,
            termination_strategy=ContactCenterTerminationStrategy(),
            selection_strategy=ContactCenterSelectionStrategy()
        )

        citizen_queries = [
            "I have a document in Arabic",
            "Can you translate this to English?",
            "Where can I find my application status?"
        ]

        for query in citizen_queries:
            print(f"\nCitizen: {query}")
            try:
                await chat.add_chat_message(ChatMessageContent(role=AuthorRole.USER, content=query))
            except Exception as e:
                print(f"[ERROR] Failed to add message: {e}")
                continue

            while True:
                try:
                    selected_agent = await chat.selection_strategy.select_agent(chat.agents, chat.history)
                    if selected_agent is None:
                        break

                    async for response in chat.invoke_agent(selected_agent):
                        if response and response.content:
                            name = getattr(response, "name", None) or "UnknownAgent"
                            print(f"{name}: {response.content}")

                    should_terminate = await chat.termination_strategy.should_agent_terminate(selected_agent, chat.history)
                    if should_terminate:
                        break

                except Exception as e:
                    print(f"[ERROR] Exception during chat: {e}")
                    break

            try:
                await chat.reset()
            except Exception as ex:
                print(f"[WARNING] Could not reset chat: {ex}")





if __name__ == "__main__":
    asyncio.run(main())
