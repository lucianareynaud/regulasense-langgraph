# RegulaSense

RegulaSense is an **iterative, regulatory-grade RAG pipeline** that marries
LangGraph's state-ful orchestration with Pydantic-AI's strict schema validation
to generate XBRL-compatible financial statements from unstructured evidence.

## Architecture Overview

RegulaSense implements a scalable, production-ready architecture that addresses the real-world challenges of regulatory compliance in financial reporting:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                        RegulaSense Architecture                         │
│                                                                         │
├─────────────┬─────────────────────────────────────────────┬────────────┤
│             │                                             │            │
│  Streamlit  │        Stateful LangGraph Orchestration     │   Vector   │
│     UI      │ ┌─────────┐  ┌─────────┐  ┌─────────────┐   │  Database  │
│  ┌───────┐  │ │         │  │         │  │             │   │ ┌────────┐ │
│  │       │◄─┼─┤ Retrieve◄──┤ Analyze ◄──┤  XBRL Draft │◄──┼─┤ Qdrant │ │
│  │       │  │ │         │  │  Gaps   │  │ w/Validation│   │ │        │ │
│  └───────┘  │ └────┬────┘  └────┬────┘  └─────────────┘   │ └────────┘ │
│             │      │  ▲         │                         │            │
│             │      └──┼─────────┘                         │            │
│             │         │                                   │            │
└─────────────┴─────────────────────────────────────────────┴────────────┘
```

### Key Technical Components

1. **Self-correcting LLM Pipeline**: Implements rigorous validation loops and iterative evidence gathering
2. **Schema Enforcement**: Every financial statement undergoes Pydantic-AI validation to ensure XBRL compliance
3. **Vector Search Integration**: Evidence retrieval with semantic search against regulatory documents
4. **Containerized Microservices**: Deployable at scale with Docker and efficient API interfaces

## Technical Stack

### Backend (API)
- FastAPI for high-performance API endpoints
- LangGraph for stateful, directed orchestration graphs
- Pydantic-AI for streaming schema validation
- OpenAI for language model inference
- Qdrant for vector storage and semantic search

### Frontend (UI)
- Streamlit for rapid visualization
- Asynchronous API integration

## Architecture Decisions

RegulaSense is designed with several key architecture principles:

1. **Separation of Concerns**: Clear boundaries between UI, orchestration, and data layers
2. **Iterative Refinement**: LangGraph enables sophisticated feedback loops for evidence gathering
3. **Strict Validation**: Pydantic models enforce regulatory compliance at runtime
4. **Horizontal Scalability**: Containerized services can scale independently

## Getting Started

```bash
# Clone the repository
git clone https://github.com/yourusername/regulasense.git
cd regulasense

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration

# Start the application
./run.sh
```

Access the UI at http://localhost:8501

## Development Roadmap

RegulaSense is designed for extensibility:

- **Taxonomy Expansion**: Support for complete XBRL taxonomies beyond demo subset
- **Multiple Regulatory Frameworks**: Extend to GDPR, IFRS, GAAP compliance
- **Multi-Agent Specialization**: Domain-specific agents for different regulatory areas
- **Enterprise Integration**: API hooks for ERP and compliance management systems

## Performance Considerations

The system is architected to handle high-throughput regulatory analysis:

- Vector database sharding for large document collections
- Asynchronous processing for concurrent document analysis
- Batch processing capabilities for overnight compliance verification

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Why LangGraph *and* Pydantic-AI?

| Concern                | Technology                             |
|------------------------|----------------------------------------|
| Looping, backtracking, human-in-the-loop checkpoints | **LangGraph** |
| Audit-trail & replayable global state           | **LangGraph** |
| Guaranteed contract fidelity (no JSON drift)    | **Pydantic-AI** |
| Early-abort on invalid tokens (stream validation)| **Pydantic-AI** |

## Design Decisions

1. **Single mutable `DDState`** keeps evidence + log messages; every node
   returns only the *delta*, enabling deterministic diffing and snapshotting.
2. **Vector store** = Qdrant (lightweight, dockerable, ANN-friendly).
3. **FastAPI boundary** isolates orchestration from presentation; any client
   (Streamlit, Dash, Next.js) can consume `/run`.
4. **Streamlit demo** is opinionated but disposable; swap for your enterprise
   portal with minimal changes.
5. **Twelve-factor config** – secrets live in `.env`, never in code.

## Quick-start

```bash
cp .env.example .env          # add your OpenAI key
./run.sh                      # builds & starts api, qdrant, ui
open http://localhost:8501    # interactive playground







```mermaid
stateDiagram-v2
    [*] --> RETRIEVE : entry
    RETRIEVE --> ANALYZE : docs\n→ messages+=log
    ANALYZE --> RETRIEVE : "CONTINUE"
    ANALYZE --> DRAFT : "DONE"
    DRAFT --> [*]      : END

    state DRAFT {
        [*] --> XBRL_AGENT : draft_statement()
        XBRL_AGENT --> [*]
    }
