def create_citations(state):
    docs = state.get("reranked_docs", [])

    citations = []

    for item in docs:
        metadata = item.get("metadata", {})

        citations.append({
            "filename": metadata.get("filename"),
            "page": metadata.get("page"),
            "chunk": metadata.get("chunk"),
            "score": item.get("score")
        })

    state["citations"] = citations

    return state