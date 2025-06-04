# Multi-Agent Azure AI Demo – Kuwait Government Showcase

This project demonstrates a real-world Azure AI multi-agent orchestration for public sector use, using **Semantic Kernel** as the orchestrator.

## 🧠 Use Case
The demo simulates a government AI contact center that:
- Answers citizen queries
- Processes uploaded documents
- Translates Arabic/English
- Stores and analyzes structured data
- Presents reports and dashboards
- Logs and manages project actions

## 👥 Agents Overview

1. **CallCenterAgent**
   - Purpose: Interacts with citizens (voice/chat)
   - Tech: Azure AI Speech + OpenAI
   - Capabilities:
     - Handles FAQs
     - Transcribes and routes queries
     - Interfaces with Document, Translation, or PMO agents

2. **DocumentAgent**
   - Purpose: Extracts structured info from documents
   - Tech: Azure Document Intelligence
   - Capabilities:
     - OCR and field extraction from forms, images, PDFs
     - Validates document type
     - Sends structured output to Fabric

3. **TranslationAgent**
   - Purpose: Enables real-time Arabic ↔ English translation
   - Tech: Azure Translator
   - Capabilities:
     - Translates incoming and outgoing messages
     - Ensures contextual and accurate translation

4. **FabricDataAgent**
   - Purpose: Stores and prepares data
   - Tech: Microsoft Fabric
   - Capabilities:
     - Ingests structured outputs from DocumentAgent
     - Cleans and stores for analysis
     - Prepares data for Power BI

5. **PowerBIReportingAgent**
   - Purpose: Creates dashboards and reports
   - Tech: Power BI
   - Capabilities:
     - Connects to Fabric data
     - Visualizes citizen interaction and document trends

6. **PMOAgent**
   - Purpose: Project and task orchestration
   - Tech: Azure Logic Apps + Functions
   - Capabilities:
     - Logs all interactions
     - Automates escalations and follow-up actions
     - Maintains audit trail

## 🔄 Agent Interaction Workflow

1. Citizen contacts **CallCenterAgent**
2. If Arabic: forward to **TranslationAgent**
3. If document: route to **DocumentAgent** → extract info → send to **FabricDataAgent**
4. **PowerBIReportingAgent** visualizes data from Fabric
5. **TranslationAgent** converts results if needed
6. **PMOAgent** logs full session and triggers workflows

## 🛠 Technologies

- Semantic Kernel (agent orchestration)
- Azure OpenAI + Speech Services
- Azure Document Intelligence
- Microsoft Translator
- Microsoft Fabric
- Power BI
- Azure Logic Apps & Functions

## 📁 File Structure

- `agents.py` — Defines multiple agents (may include other scenarios too)
- `orchestrator.py` — Coordinates agent flow using Semantic Kernel
- `README.md` — High-level guidance for purpose and agent definitions
