"""
LangGraph definition for iterative retrieval → enrichment → validation loop.
"""
from typing import TypedDict, List, Annotated
import operator, asyncio
from langgraph.graph import StateGraph, END
from langchain_core.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from qdrant_client import QdrantClient
from app.config import settings
from app.agents.xbrl_agent import draft_statement

llm = ChatOpenAI(model=settings.openai_model, temperature=0.0)

client = QdrantClient(url=settings.qdrant_url)
COLL = settings.collection_name

class DDState(TypedDict):
    messages: Annotated[List[str], operator.add]
    evidence: Annotated[List[str], operator.add]  # doc chunks
    complete: bool

# ------------- Node definitions ---------------------------------
def retrieve(state: DDState) -> DDState:
    query = state["messages"][-1]
    hits = client.search(collection_name=COLL, query_text=query, limit=5)
    docs = [h.payload["text"] for h in hits]
    return {"evidence": docs, "messages": [f"Retrieved {len(docs)} docs."]}

def gap_analyzer(state: DDState) -> DDState:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Decide if evidence is sufficient. Reply DONE or CONTINUE."),
            ("user", "\n".join(state["evidence"])),
        ]
    )
    resp = llm.invoke(prompt.format())
    done = "DONE" in resp.content
    return {"messages": [resp.content], "complete": done}

async def draft_xbrl(state: DDState) -> DDState:
    digest = "\n".join(state["evidence"])
    result = await draft_statement(digest)  # Pydantic-AI ensures validity
    return {"messages": [result.model_dump_json()], "complete": True}

def route(state: DDState) -> str:
    return "draft" if state["complete"] else "retrieve"

# ------------- Build the graph ----------------------------------
graph = StateGraph(DDState)
graph.add_node("retrieve", retrieve)
graph.add_node("analyze", gap_analyzer)
graph.add_async_node("draft", draft_xbrl)

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "analyze")
graph.add_conditional_edge("analyze", route, {"retrieve": "retrieve", "draft": "draft"})
graph.add_edge("draft", END)

due_diligence_flow = graph.compile() 