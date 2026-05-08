import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "vector_database.json")


def load_database():
    if not os.path.exists(DB_FILE):
        return []

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data if isinstance(data, list) else []

    except Exception:
        return []


def save_database(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_chunks_to_vector_store(chunks, document_id=None, replace_document=True):
    database = load_database()

    if document_id and replace_document:
        database = [
            item for item in database
            if item.get("document_id") != document_id
            and item.get("metadata", {}).get("document_id") != document_id
        ]

    stored_count = 0

    for index, chunk in enumerate(chunks, start=1):
        text = str(chunk.get("text", "")).strip()
        metadata = chunk.get("metadata", {})

        if not text:
            continue

        chunk_document_id = metadata.get("document_id") or document_id

        doc_id = (
            f"{chunk_document_id}_"
            f"page_{metadata.get('page', 'na')}_"
            f"chunk_{metadata.get('chunk', index)}"
        )

        database.append({
            "id": doc_id,
            "document_id": chunk_document_id,
            "text": text,
            "metadata": metadata
        })

        stored_count += 1

    save_database(database)

    return stored_count


def search_vector_store(query, top_k=5, document_id=None):
    database = load_database()

    if document_id:
        database = [
            item for item in database
            if item.get("document_id") == document_id
            or item.get("metadata", {}).get("document_id") == document_id
        ]

    if not database:
        return []

    texts = [item.get("text", "") for item in database]
    query = str(query or "").strip()

    if not query:
        return []

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=5000
    )

    matrix = vectorizer.fit_transform(texts + [query])

    doc_vectors = matrix[:-1]
    query_vector = matrix[-1]

    scores = cosine_similarity(query_vector, doc_vectors).flatten()

    scored_results = []

    for index, score in enumerate(scores):
        item = database[index]

        scored_results.append({
            "id": item.get("id"),
            "document_id": item.get("document_id") or item.get("metadata", {}).get("document_id"),
            "text": item.get("text", ""),
            "metadata": item.get("metadata", {}),
            "score": round(float(score), 4)
        })

    scored_results.sort(key=lambda x: x["score"], reverse=True)

    return scored_results[:top_k]


def get_document_chunks(document_id):
    database = load_database()

    return [
        item for item in database
        if item.get("document_id") == document_id
        or item.get("metadata", {}).get("document_id") == document_id
    ]


def clear_vector_store(document_id=None):
    if document_id:
        database = load_database()
        database = [
            item for item in database
            if item.get("document_id") != document_id
            and item.get("metadata", {}).get("document_id") != document_id
        ]
        save_database(database)
        return True

    save_database([])
    return True