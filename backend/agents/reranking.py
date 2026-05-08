def rerank_documents(state):
    docs = state.get("retrieved_docs", [])

    docs = sorted(
        docs,
        key=lambda item: item.get("score", 0),
        reverse=True
    )

    state["reranked_docs"] = docs[:3]

    return state