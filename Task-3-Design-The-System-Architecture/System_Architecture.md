# System Architecture

## AI-Based Startup Idea Validator with Market Analysis Assistance

**Milestone:** 1 --- System Architecture Design\
**Document type:** Technical design document\
**Status:** Proposed architecture for initial implementation

------------------------------------------------------------------------

## 1. Project Overview and Architecture Objective

### 1.1 Project overview

Entrepreneurs often have startup ideas but find it difficult to evaluate
market demand, business feasibility, competitors, and execution risks
before investing significant time and money. This project proposes an
AI-Based Startup Idea Validator with Market Analysis Assistance.

The system accepts a startup idea in a short description and initiates a
structured multi-agent workflow. A Web Search Agent retrieves relevant
online information. Specialized agents analyze market opportunities,
target customers, competitors, SWOT, and risks. An MVP Recommendation
Agent proposes features for an initial product, and a Report Generation
Agent combines the findings into a startup validation report with
go-to-market recommendations.

### 1.2 Architecture objective

The objective of this architecture is to define the main software
components, their responsibilities, and the flow of information from
idea submission to report generation.

The proposed architecture should: - Accept a startup idea and relevant
business details through a user interface. - Convert the submitted
description into structured data using a Large Language Model (LLM). -
Retrieve relevant, current online information through a web search
API. - Coordinate specialized AI agents and pass analysis context
between them. - Produce a structured report that explains findings,
recommendations, and evidence limitations. - Keep components modular so
that they can be developed and tested independently.

**Scope note:** The project brief identifies the required modules and
capabilities but does not mandate a particular framework, LLM provider,
database, or orchestration library. The technologies in this document
are proposed choices for implementation, not fixed requirements from the
brief.

------------------------------------------------------------------------

## 2. High-Level System Architecture Diagram

The following diagram shows the major layers and the direction of
information flow.

``` mermaid
flowchart TD
    U[User / Entrepreneur] --> UI[Frontend: Startup Idea Submission UI]
    UI -->|Idea details via HTTP| API[Backend API]
    API --> VAL[Input Validation]
    VAL --> LLM[LLM: Structured Idea Extraction]
    LLM --> ORCH[Multi-Agent Orchestrator]

    ORCH --> WS[Web Search Agent]
    WS --> SEARCH[Web Search API: Tavily or Equivalent]
    SEARCH -->|Results, snippets, source URLs| WS
    WS --> CONTEXT[Shared Analysis Context]

    CONTEXT --> MA[Market Analysis Agent]
    CONTEXT --> CA[Competitor Analysis Agent]
    MA --> CONTEXT
    CA --> CONTEXT

    CONTEXT --> SWOT[SWOT and Risk Analysis Agent]
    SWOT --> CONTEXT
    CONTEXT --> MVP[MVP Recommendation Agent]
    MVP --> CONTEXT

    CONTEXT --> REPORT[Report Generation Agent]
    REPORT --> RESULT[Structured Startup Validation Report]
    RESULT --> API
    API --> UI

    API -. Optional persistence .-> DB[(Database / Storage)]
    REPORT -. Optional save .-> DB
```

### Diagram explanation

1.  The user submits an idea through the frontend.
2.  The backend validates the submitted fields and requests structured
    extraction from the LLM.
3.  The orchestrator starts and coordinates the agent workflow.
4.  The Web Search Agent uses the search API and returns source-linked
    findings.
5.  Market and competitor analysis use the collected evidence and
    structured idea.
6.  SWOT/risk and MVP analysis use the preceding outputs.
7.  The Report Generation Agent compiles the findings and returns the
    report through the backend to the frontend.
8.  A database is optional for the first version and can be added to
    save ideas, analysis outputs, and reports.

------------------------------------------------------------------------

## 3. Detailed Component Architecture Diagram

This diagram expands the backend and agent layer. It is a logical
design: the components do not need to run as separate servers.

``` mermaid
flowchart TB
    subgraph FRONTEND["Frontend Layer"]
        FORM[Idea Submission Form]
        STATUS[Analysis Progress / Status]
        VIEW[Report Dashboard]
        FORM --> STATUS
        STATUS --> VIEW
    end

    subgraph BACKEND["Backend Layer"]
        API[FastAPI REST API]
        VALIDATE[Request Validation: Pydantic]
        EXTRACT[Structured Idea Extraction]
        API --> VALIDATE --> EXTRACT
    end

    subgraph AI["AI and Orchestration Layer"]
        LLM[LLM Service]
        ORCH[Agent Orchestrator]
        CTX[(Shared Analysis Context)]
        EXTRACT --> LLM --> ORCH
        ORCH <--> CTX
    end

    subgraph RESEARCH["Research Layer"]
        WSA[Web Search Agent]
        TAVILY[Tavily Search API]
        WSA <--> TAVILY
    end

    subgraph AGENTS["Analysis Agents"]
        MARKET[Market Analysis Agent]
        COMP[Competitor Analysis Agent]
        SWOT[SWOT and Risk Agent]
        MVP[MVP Recommendation Agent]
        REPORT[Report Generation Agent]
    end

    subgraph STORAGE["Optional Persistence"]
        DB[(SQLite initially / PostgreSQL later)]
    end

    FORM --> API
    ORCH --> WSA
    WSA --> CTX
    CTX --> MARKET
    CTX --> COMP
    MARKET --> CTX
    COMP --> CTX
    CTX --> SWOT --> CTX
    CTX --> MVP --> CTX
    CTX --> REPORT
    REPORT --> VIEW
    API -. optional .-> DB
    REPORT -. optional .-> DB
```

### Component interaction notes

-   The **backend API** is the entry point for requests from the
    frontend.
-   The **LLM service** extracts structured fields from the founder's
    description and supports agent reasoning.
-   The **orchestrator** decides when each agent runs and passes the
    shared context between agents.
-   The **Web Search Agent** calls Tavily or an equivalent API; the
    search provider is an external service.
-   The **analysis agents** have separate responsibilities and should
    return structured outputs.
-   The **shared analysis context** holds the submitted idea, search
    results, and outputs generated by earlier agents.
-   The **report dashboard** displays the result returned by the
    backend.
-   **Storage is optional** for the initial prototype. If implemented,
    it can persist the idea, sources, analysis, and report.

------------------------------------------------------------------------

## 4. Components and Responsibilities

  -----------------------------------------------------------------------
  Component                           Responsibilities
  ----------------------------------- -----------------------------------
  **User / Entrepreneur**             Supplies the startup idea and
                                      relevant business context.

  **Frontend UI**                     Collects the idea description,
                                      target customers, industry, and
                                      optional details; validates
                                      required fields; shows progress and
                                      the final report.

  **Backend API**                     Receives frontend requests,
                                      validates payloads, calls the LLM
                                      and orchestrator, handles errors,
                                      and returns results.

  **LLM service**                     Converts free-text input into
                                      structured idea data and supports
                                      language-based analysis. It should
                                      not be treated as proof that market
                                      claims are true.

  **Multi-Agent Orchestrator**        Controls the workflow, passes
                                      context, tracks agent status,
                                      handles failures, and collects
                                      agent outputs.

  **Web Search Agent**                Creates search queries, calls the
                                      web search API, filters or
                                      organizes relevant results, and
                                      preserves source URLs/snippets.

  **Web Search API**                  External service that returns web
                                      results for market, industry,
                                      customer-problem, and competitor
                                      queries. Tavily is the proposed
                                      option.

  **Market Analysis Agent**           Evaluates market demand signals,
                                      industry trends, customer segments,
                                      and potential opportunities using
                                      available evidence.

  **Competitor Analysis Agent**       Identifies similar
                                      businesses/products and compares
                                      offerings, positioning, and
                                      possible differentiation gaps.

  **SWOT and Risk Analysis Agent**    Produces strengths, weaknesses,
                                      opportunities, and threats;
                                      identifies business, technical,
                                      operational, and adoption risks.

  **MVP Recommendation Agent**        Prioritizes essential features for
                                      a minimum viable product and
                                      proposes a small initial scope to
                                      test assumptions.

  **Report Generation Agent**         Combines agent outputs into a
                                      readable report, including
                                      evidence, assumptions, risks, MVP
                                      suggestions, and go-to-market
                                      recommendations.

  **Shared Analysis Context**         Holds the structured idea, search
                                      evidence, and intermediate agent
                                      results for use across the
                                      pipeline.

  **Database / Storage (optional)**   Stores submitted ideas, source
                                      metadata, intermediate outputs, and
                                      reports for later access.

  **Report Dashboard**                Displays the final report and, if
                                      implemented, provides export or
                                      download functionality.
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 5. Step-by-Step Data Flow

1.  **Idea submission:** The founder enters a short startup idea
    description and relevant fields such as industry and target
    customers.
2.  **Frontend validation:** The UI checks required fields and sends the
    data to the backend through an HTTP request.
3.  **Backend validation:** The backend validates the request structure
    and rejects missing or malformed required input.
4.  **Structured extraction:** The LLM converts the free-text idea into
    fields such as problem, proposed solution, target users, industry,
    value proposition, and assumptions. Unknown fields should remain
    unknown rather than being invented.
5.  **Workflow initialization:** The orchestrator creates a shared
    analysis context for the request.
6.  **Web research:** The Web Search Agent formulates relevant queries
    and calls Tavily or an equivalent web search API.
7.  **Evidence collection:** Search results are organized with titles,
    snippets, URLs, and dates when provided. The system retains source
    information so findings can be checked.
8.  **Market analysis:** The Market Analysis Agent evaluates demand
    signals, industry trends, and customer segments using the structured
    idea and available search evidence.
9.  **Competitor analysis:** The Competitor Analysis Agent identifies
    and compares existing alternatives and possible gaps.
10. **SWOT and risk assessment:** The SWOT and Risk Analysis Agent uses
    the idea and previous findings to produce a structured SWOT analysis
    and identify execution risks.
11. **MVP recommendations:** The MVP Recommendation Agent proposes a
    prioritized set of essential features and assumptions to test with
    early users.
12. **Report generation:** The Report Generation Agent compiles the
    findings into a structured report, including market opportunity,
    competitor insights, SWOT, risks, MVP scope, and go-to-market
    suggestions.
13. **Response and display:** The backend returns the report to the
    frontend, which displays it to the founder.
14. **Optional persistence:** If storage is enabled, the system saves
    the idea, source references, agent outputs, and final report.

### Proposed execution order

The Web Search Agent runs first after idea structuring. The Market
Analysis Agent and Competitor Analysis Agent may run in parallel once
search results are available. The SWOT and Risk Analysis Agent then uses
their outputs, followed by the MVP Recommendation Agent and Report
Generation Agent.

This is a proposed orchestration strategy. The project brief requires
coordination and context passing but does not prescribe the exact
scheduling mechanism.

------------------------------------------------------------------------

## 6. Proposed Technology Stack

The project brief does not specify a mandatory stack. The following is a
practical proposal for an initial Python-based implementation.

  -----------------------------------------------------------------------
  Layer                   Proposed technology     Reason for selection
  ----------------------- ----------------------- -----------------------
  Frontend                React or Next.js        Build the submission
                                                  form, status view, and
                                                  report dashboard.

  Backend                 Python with FastAPI     Create API endpoints
                                                  and coordinate
                                                  application logic.

  Request / output        Pydantic                Validate incoming data
  validation                                      and structured agent
                                                  outputs.

  LLM                     An API-accessible LLM   Structure the idea and
                          selected by the team    support agent analysis.

  Web search              Tavily Search API or    Retrieve relevant
                          equivalent              online results and
                                                  source URLs.

  Agent orchestration     Custom Python           Keep the first workflow
                          orchestrator initially  understandable and
                                                  testable.

  Database                SQLite for a simple     Persist ideas and
                          prototype; PostgreSQL   reports if persistence
                          if needed later         is implemented.

  Diagram documentation   Mermaid in Markdown     Store editable
                                                  architecture diagrams
                                                  in GitHub.

  Version control         Git and GitHub          Collaborate, review
                                                  changes, and maintain
                                                  documentation.
  -----------------------------------------------------------------------

**Implementation note:** These are recommendations rather than
requirements from the attached project statement. The team should
confirm available API access, model cost, and deployment constraints
before finalizing providers.

------------------------------------------------------------------------

## 7. Design Considerations and Assumptions

### 7.1 Modularity

Each agent should have a clearly defined responsibility and a
predictable input/output structure. This makes individual agents easier
to develop, test, and improve.

### 7.2 Evidence and source traceability

Market and competitor findings should include source URLs and supporting
snippets wherever possible. The report should distinguish retrieved
evidence from the LLM's interpretation.

### 7.3 Structured data exchange

The idea and agent results should use defined JSON-like schemas.
Consistent output formats make it easier to pass information between
agents and generate the final report.

### 7.4 Error handling

The system should handle search API failures, rate limits, timeouts,
empty results, and invalid LLM output. If reliable evidence is
unavailable, the report should explicitly state the limitation instead
of fabricating information.

### 7.5 Security

API keys must be stored in backend environment variables or a secrets
manager. They must not be exposed in frontend code or committed to the
GitHub repository. User-submitted data should be validated before
processing.

### 7.6 Reliability and uncertainty

An LLM can produce incorrect or unsupported claims. The system should
avoid presenting generated estimates as verified market statistics and
should label assumptions, evidence gaps, and uncertainty clearly.
Startup validation is decision support, not a guarantee of business
success.

### 7.7 Scalability

For the initial milestone, a single backend and a custom orchestrator
should be sufficient. Separate services, queues, or more advanced
orchestration frameworks can be considered if processing volume grows.

### 7.8 Storage

Persistent storage is optional for the initial architecture unless
required by the team. The first prototype can return a report without
saving it; a database can be introduced when saved workspaces or report
history are implemented.

### 7.9 Proposed assumptions

-   The user submits a short description and may provide additional
    context.
-   The backend can access the selected LLM and web search APIs.
-   The web search provider returns results that can be used as research
    leads, not guaranteed proof of demand.
-   The agents share a common analysis context managed by the
    orchestrator.
-   The workflow is primarily sequential, with market and competitor
    analysis allowed to run in parallel.
-   A human founder remains responsible for verifying important findings
    and making the final business decision.

------------------------------------------------------------------------

## Conclusion

The proposed architecture uses a frontend, backend API, LLM service, web
search integration, and a coordinated set of specialized AI agents to
transform a startup idea into a structured validation report. The
orchestrator manages the workflow and shares information between agents,
while source tracking and explicit uncertainty handling help make the
report more transparent. The modular design supports incremental
development, starting with idea submission and web search before adding
the remaining analysis and reporting capabilities.
