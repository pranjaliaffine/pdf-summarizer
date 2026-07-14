# pdf summarizer

Agentic workflow architecture exported from **[Agentic LaunchPad](https://github.com)** by Affine Analytics.

> This repository is a scaffold generated from an interactive architecture interview and visual workflow builder. Implement each agent step per the plan below.

## At a glance

- **Session:** `aeaf7b4d-35ca-43e0-9e4d-974e8ef12064`
- **Steps:** 6
- **Connections:** 5
- **Exported:** 2026-07-14 16:32 UTC

## Problem statement

pdf summarizer

## Requirements

### Interview summary

Workflow configured with Entity Extraction Agent and KYC Policy Completeness Validator. User specified Entity Extraction Agent should use the uploaded file name as the identifier for filename input. User specified the validator should start with a standard corporate KYC policy template for completeness checks. User also stated compliance/quality handling should be configured per case with analyst review. Catalog-aligned notes indicate these agents commonly integrate with Azure OpenAI, Azure Blob Storage, and Azure SQL Server, but those remain unconfirmed as user requirements.

### Architecture blueprint

# Overview
This architecture is a document-processing workflow for a PDF summarizer use case that has been configured around two reusable Affine components already identified in discovery:

1. Entity Extraction Agent
2. KYC Policy Completeness Validator

Although the problem statement says "pdf summarizer," the confirmed workflow is specifically oriented to corporate KYC document processing. The system accepts an uploaded PDF, uses the uploaded file name as the document identifier, extracts structured KYC-relevant entities from the document, validates completeness against a standard corporate KYC policy template, and routes the case for analyst review on a per-case basis for compliance and quality handling.

Because the completed spec leaves most nonfunctional requirements unconfirmed, this Phase 3-ready package stays tightly grounded in what was explicitly stated:
- input is an uploaded PDF
- filename should be the uploaded file name
- extraction is performed by Entity Extraction Agent
- completeness checking is performed by KYC Policy Completeness Validator
- validator should start from a standard corporate KYC policy template
- compliance/quality handling is configured per case with analyst review
- Azure OpenAI, Azure Blob Storage, and Azure SQL Server are catalog-aligned hints, not confirmed requirements

# End-to-end flow
1. A user uploads a PDF through an intake gateway.
2. The gateway registers the case and passes the uploaded file plus the uploaded file name as the identifier.
3. The Entity Extraction Agent processes the PDF and extracts structured KYC-related entities and relationships.
4. The extracted output is passed to the KYC Policy Completeness Validator.
5. The validator evaluates the extracted content against a standard corporate KYC policy template to determine completeness.
6. The case is routed to an analyst for per-case compliance and quality review.
7. The reviewed result is finalized as the case output, including extracted structured data and completeness findings suitable for downstream use.

# Core components
## 1. PDF intake gateway
A front-door service receives the uploaded PDF and initiates processing. Its key responsibility is to preserve the uploaded file name and pass it forward as the identifier required by the Entity Extraction Agent.

## 2. Entity Extraction Agent
This reusable Affine agent is the primary document understanding component. In this engagement it is configured to:
- accept the uploaded PDF
- use the uploaded file name as the filename input / identifier
- extract structured KYC-relevant entities from the document

Catalog hints indicate this agent commonly uses Azure OpenAI and can persist structured JSON for SQL-backed workflows, but those integrations are not treated as mandatory here.

## 3. KYC Policy Completeness Validator
This reusable Affine validator checks whether the extracted KYC information is complete enough relative to policy expectations. In this engagement it is configured to:
- consume the extraction output
- start with a standard corporate KYC policy template
- assess completeness of required KYC information
- produce completeness findings that can support case review

## 4. Analyst review step
A human analyst reviews each case for compliance and quality handling. This is the explicit human-in-the-loop gate confirmed in discovery. The analyst reviews extraction and completeness results per case before finalization.

## 5. Final case output
The workflow ends with a finalized case package containing:
- document identifier based on uploaded file name
- extracted structured KYC information
- completeness assessment against the standard corporate KYC policy template
- analyst-reviewed disposition

# Data & integrations
## Confirmed data objects
The architecture can be grounded around the following confirmed artifacts:
- uploaded PDF
- uploaded file name used as identifier
- extracted structured KYC data
- standard corporate KYC policy template
- completeness validation findings
- analyst review outcome

## Confirmed integrations
No external system integration was explicitly confirmed by the user.

## Catalog-aligned but unconfirmed integrations
The catalog hints suggest the following common implementation pattern for the selected agents:
- Azure OpenAI
- Azure Blob Storage
- Azure SQL Server

These should be treated as implementation options, not locked requirements, until the client confirms source/target systems and hosting preferences.

# Orchestration & reliability
## Orchestration model
The confirmed workflow is sequential:
- intake
- extraction
- completeness validation
- analyst review
- finalization

This is appropriate because the validator depends on extraction output, and analyst review depends on both machine-generated outputs.

## Reliability considerations
Given the limited confirmed requirements, the reliability design should focus on simple operational controls:
- preserve the uploaded file name exactly as received for traceability
- maintain case-level linkage between source PDF, extraction output, validation findings, and analyst decision
- fail the case into review if extraction or validation output is incomplete or unusable
- keep analyst review as the explicit control point for compliance/quality handling

## Quality controls
The main quality control is the human analyst review per case. The validator provides a structured pre-review completeness check using the standard corporate KYC policy template, helping the analyst identify missing mandatory information.

# Deployment
Deployment platform was not confirmed in the spec.

For Phase 3 planning, the architecture should therefore be treated as deployment-agnostic, with implementation details deferred until the client confirms environment preferences. If the team chooses to align with the selected agents' common pattern, Azure-based deployment would be a natural option, but this remains unconfirmed.

# Risks & open assumptions
## Risks
- The stated problem is "pdf summarizer," but the configured workflow is actually a KYC document extraction and completeness-validation flow. The intended business output may need clarification.
- No latency, throughput, or scale requirements were provided.
- No explicit storage, system-of-record, or downstream delivery target was confirmed.
- No model preference or deployment platform was confirmed.
- The exact structure of the final summary/output package is not defined.

## Open assumptions used in this package
- The uploaded PDF is the primary input artifact.
- The uploaded file name is the canonical case/document identifier for processing.
- The standard corporate KYC policy template is the initial completeness baseline.
- Analyst review is mandatory per case for compliance/quality handling.
- The workflow should stop at analyst-reviewed finalization rather than proceeding into any unconfirmed downstream risk analysis or persistence layer.

## Architecture summary

This Phase 3 architecture keeps a single left-to-right flow from PDF upload to finalized case output, aligned to the confirmed ArchitectureSpec rather than the generic problem title. The workflow is centered on corporate KYC document processing: an intake gateway accepts the uploaded PDF, preserves the uploaded file name as the identifier, then passes the document into extraction and completeness validation before mandatory analyst review.

The main path is: PDF Intake Gateway -> Entity Extraction -> KYC Policy Completeness Validation -> Analyst Review Gate -> Analyst Review -> Final Case Output. The human-in-the-loop behavior is implemented as an explicit routing gate followed by a human review node because the spec states compliance and quality handling must be configured per case with analyst review. The validator is configured against a standard corporate KYC policy template, and the final output contains the reviewed extraction and completeness package.

Reuse is limited because the provided Azure AI Search catalog matches do not include the two spec-named agents as actual available catalog entries in this prompt payload. Although the interview draft referenced agent_ids for Entity Extraction Agent and KYC Policy Completeness Validator, those ids were not present in the supplied catalog matches, so they were conservatively marked as build rather than reuse/adapt. The only nearby catalog option was Document Ingestion Agent, but its function summary is broader and weakly scored, so it was not selected. Orchestration is therefore a straightforward sequential workflow with explicit human approval, and the Azure OpenAI, Azure Blob Storage, and Azure SQL Server references remain integration hints only, not committed dependencies.

Primary risks are catalog ambiguity and scope drift: the solution is called a PDF summarizer, but the confirmed flow is actually KYC extraction plus completeness validation. If the missing catalog entries are later confirmed, the extraction and validation nodes can be converted from build to reuse with minimal graph change. Another risk is unconfirmed integration architecture, since storage, model hosting, and persistence technologies were mentioned only as catalog-aligned possibilities rather than approved requirements.

## Workflow overview

This architecture has **6** step(s) and **5** connection(s).

### Execution flow

- **PDF Intake Gateway** → *uploaded PDF + uploaded file name identifier* → **Entity Extraction Agent**
- **Entity Extraction Agent** → *structured KYC entities* → **KYC Policy Completeness Validator**
- **KYC Policy Completeness Validator** → *completeness findings + extracted data* → **Analyst Review Gate**
- **Analyst Review Gate** → *case routed for mandatory human review* → **Analyst Review**
- **Analyst Review** → *approved or amended case package* → **Final Case Output**

## Agents & steps

### PDF Intake Gateway

*gateway* · **build**

Receives uploaded PDF, validates file presence, and passes uploaded file name as the case identifier

*Rationale:* The catalog ingestion agent is only a weak match and the spec requires a simple intake gateway with filename-as-identifier behavior rather than a broader ingestion component.

### Entity Extraction Agent

*custom* · **build**

Extracts structured KYC-relevant entities from the uploaded PDF using the uploaded file name as identifier

*Rationale:* The spec names an Entity Extraction Agent, but no matching catalog agent_id was provided in the search results, so this step must be modeled as a custom build for now.

### KYC Policy Completeness Validator

*custom* · **build**

Evaluates extracted content against a standard corporate KYC policy template for completeness

*Rationale:* The spec names a KYC Policy Completeness Validator, but no matching catalog entry was supplied, so it cannot be marked as reuse or adapt.

### Analyst Review Gate

*gateway* · **build**

Routes every case to human review for per-case compliance and quality handling

*Rationale:* This is a workflow routing control required by the hitl behavior and is not represented by a reusable catalog agent.

### Analyst Review

*human* · **build**

Analyst reviews extraction results and completeness findings and determines final case disposition

*Rationale:* Human compliance and quality review is explicitly required per case and should remain a human step rather than an agent reuse decision.

### Final Case Output

*custom* · **build**

Publishes the finalized analyst-reviewed extraction and completeness package

*Rationale:* Final packaging and publication of the reviewed case output is a lightweight orchestration/output component not covered by the catalog matches.

## Reuse decisions

- **PDF Intake Gateway** — `build` → custom
  - The catalog ingestion agent is only a weak match and the spec requires a simple intake gateway with filename-as-identifier behavior rather than a broader ingestion component.
- **Entity Extraction Agent** — `build` → custom
  - The spec names an Entity Extraction Agent, but no matching catalog agent_id was provided in the search results, so this step must be modeled as a custom build for now.
- **KYC Policy Completeness Validator** — `build` → custom
  - The spec names a KYC Policy Completeness Validator, but no matching catalog entry was supplied, so it cannot be marked as reuse or adapt.
- **Analyst Review Gate** — `build` → custom
  - This is a workflow routing control required by the hitl behavior and is not represented by a reusable catalog agent.
- **Analyst Review** — `build` → custom
  - Human compliance and quality review is explicitly required per case and should remain a human step rather than an agent reuse decision.
- **Final Case Output** — `build` → custom
  - Final packaging and publication of the reviewed case output is a lightweight orchestration/output component not covered by the catalog matches.

## Catalog matches

- **Document Ingestion Agent** (`document_ingestion_agent`) — score 0.02
  - Matched for: pdf summarizer

Workflow configured with Entity Extraction Agent and KYC Policy
  - Corporate KYC document ingestion entry point: accepts uploaded PDF, DOCX, TXT, or XLSX via file path or blob storage, detects file type, extracts and normalizes text (with OCR for scanned PDFs), chunks content, and emits document_id and text_content for downstream entity extraction and policy valida
- **Document Ingestion Agent** (`document-ingestion-agent`) — score 0.02
  - Matched for: pdf summarizer

Workflow configured with Entity Extraction Agent and KYC Policy
  - Corporate KYC document ingestion entry point: accepts uploaded PDF, DOCX, TXT, or XLSX via file path or blob storage, detects file type, extracts and normalizes text (with OCR for scanned PDFs), chunks content, and emits document_id and text_content for downstream entity extraction and policy valida
- **Generation Prompt Author** (`generation-prompt-author-v2-1-0`) — score 0.01
  - Matched for: pdf summarizer

Workflow configured with Entity Extraction Agent and KYC Policy
  - Azure vision+text agent that writes per-PDP-image-type multimodal prompts (or per-role directives) from reference photos and PDF excerpts before image generation.
- **RAG Document Retriever** (`rag_document_retriever`) — score 0.01
  - Matched for: pdf summarizer

Workflow configured with Entity Extraction Agent and KYC Policy
  - Retrieves the most relevant passages from an indexed document corpus for a user query, returning ranked chunks with source citations for grounded answering.
- **Generation Prompt Author** (`generation_prompt_author`) — score 0.01
  - Matched for: pdf summarizer

Workflow configured with Entity Extraction Agent and KYC Policy
  - Azure vision+text agent that writes per-PDP-image-type multimodal prompts (or per-role directives) from reference photos and PDF excerpts before image generation.

## Open questions

- Should the final output include a natural-language summary in addition to structured extraction and completeness findings, given the original problem statement says pdf summarizer?

## Validation notes

Overall status: **warn**

- [warn] Should the final output include a natural-language summary in addition to structured extraction and completeness findings, given the original problem statement says pdf summarizer?

## Repository contents

| Path | Description |
|------|-------------|
| `README.md` | This overview |
| `workflow.json` | Full architecture graph, reuse decisions, and layout |
| `session.json` | Interview spec and session metadata (when available) |
| `agents/*.json` | Per-step scaffold files for implementation |

## Next steps

1. Review the architecture summary and agent steps above
2. Open `workflow.json` for the complete graph and reuse decisions
3. Implement each step under `agents/` using your runtime of choice
4. Wire integrations and HITL paths described in the requirements

---
*Generated by Agentic LaunchPad on 2026-07-14 16:32 UTC*