from typing import TypedDict, List, Dict, Any, Optional, Union
from langgraph.graph import StateGraph, END

from agents.query_analysis import analyze_query
from agents.retrieval import retrieve_documents
from agents.reranking import rerank_documents
from agents.generation import generate_answer_from_state
from agents.citation import create_citations


class AgentState(TypedDict):
    question: str
    document_id: Optional[str]
    analyzed_query: Dict[str, Any]
    retrieved_docs: List[Dict[str, Any]]
    reranked_docs: List[Dict[str, Any]]
    answer: str
    citations: List[Dict[str, Any]]
    retrieval_error: Optional[str]


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("query_analysis_agent", analyze_query)
    graph.add_node("retrieval_agent", retrieve_documents)
    graph.add_node("reranking_agent", rerank_documents)
    graph.add_node("generation_agent", generate_answer_from_state)
    graph.add_node("citation_agent", create_citations)

    graph.set_entry_point("query_analysis_agent")

    graph.add_edge("query_analysis_agent", "retrieval_agent")
    graph.add_edge("retrieval_agent", "reranking_agent")
    graph.add_edge("reranking_agent", "generation_agent")
    graph.add_edge("generation_agent", "citation_agent")
    graph.add_edge("citation_agent", END)

    return graph.compile()


rag_graph = build_graph()


def run_agent_graph(input_data: Union[str, Dict[str, Any]]):
    if isinstance(input_data, dict):
        question = input_data.get("question", "")
        document_id = input_data.get("document_id")
    else:
        question = input_data
        document_id = None

    initial_state = {
        "question": question,
        "document_id": document_id,
        "analyzed_query": {},
        "retrieved_docs": [],
        "reranked_docs": [],
        "answer": "",
        "citations": [],
        "retrieval_error": None
    }

    final_state = rag_graph.invoke(initial_state)

    return final_state