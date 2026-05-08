from services.vector_store import search_vector_store, get_document_chunks


def _is_greeting_query(query):
    q = (query or "").strip().lower()
    return q in ["hello", "hi", "hey", "hii", "helo", "good morning", "good evening", "good afternoon"]


def _is_broad_document_query(query):
    q = (query or "").strip().lower()

    keywords = [
        "what is mentioned",
        "what details",
        "details",
        "mentioned",
        "summary",
        "summarize",
        "about document",
        "overview",
        "agent",
        "agents",
        "mcp",
        "backend",
        "frontend",
        "requirements",
        "deliverables"
    ]

    return any(keyword in q for keyword in keywords)


def retrieve_documents(state):
    analyzed_query = state.get("analyzed_query", {})
    query = analyzed_query.get("clean_query") or state.get("question", "")
    document_id = state.get("document_id")

    if _is_greeting_query(query):
        state["retrieved_docs"] = []
        return state

    if not document_id:
        state["retrieved_docs"] = []
        state["retrieval_error"] = "missing_document_id"
        return state

    if _is_broad_document_query(query):
        state["retrieved_docs"] = get_document_chunks(document_id)[:12]
        return state

    results = search_vector_store(
        query=query,
        top_k=8,
        document_id=document_id
    )

    if not results:
        results = get_document_chunks(document_id)[:8]

    state["retrieved_docs"] = results

    return state