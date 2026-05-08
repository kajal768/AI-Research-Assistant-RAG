import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

FALLBACK_NOT_FOUND = "This information is not available in the uploaded document."


def clean_text(text):
    return str(text or "").strip()


def is_greeting(question):
    q = clean_text(question).lower()

    greetings = [
        "hello",
        "hi",
        "hey",
        "hii",
        "helo",
        "good morning",
        "good afternoon",
        "good evening"
    ]

    return q in greetings


def get_context_from_docs(docs):
    context_parts = []

    for item in docs:
        text = clean_text(item.get("text", ""))
        metadata = item.get("metadata", {})

        filename = metadata.get("filename", "Uploaded document")
        page = metadata.get("page", "")

        if text:
            source_info = f"[Source: {filename}"
            if page:
                source_info += f", Page {page}"
            source_info += "]"

            context_parts.append(f"{source_info}\n{text}")

    return "\n\n".join(context_parts).strip()


def format_sources(docs):
    sources = []
    seen = set()

    for item in docs:
        metadata = item.get("metadata", {})
        filename = metadata.get("filename", "Uploaded document")
        page = metadata.get("page")

        source = filename

        if page:
            source += f", Page {page}"

        key = source.lower()

        if key not in seen:
            sources.append(source)
            seen.add(key)

    if not sources:
        return ""

    source_text = "\n\nSources:\n"

    for source in sources[:5]:
        source_text += f"- {source}\n"

    return source_text.strip()


def generate_with_groq(question, context):
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    if not api_key:
        return (
            "Groq API key is missing. Please add GROQ_API_KEY in your .env file."
        )

    client = Groq(api_key=api_key)

    prompt = f"""
You are a professional Document Q&A RAG assistant.

Rules:
1. Answer ONLY using the uploaded document context.
2. Do NOT use outside knowledge.
3. If the answer is not present in the context, say exactly:
   "{FALLBACK_NOT_FOUND}"
4. Be clear, natural, and user-friendly.
5. Do not dump raw document text.
6. If the user asks for summary/details, provide clean bullet points.
7. If the user asks for skills, education, experience, projects, contact details, requirements, deliverables, dates, amounts, names, or any specific information, extract it from the context.
8. Keep answer concise but complete.
9. Do not invent anything.

Uploaded Document Context:
{context}

User Question:
{question}

Final Answer:
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You answer questions only from uploaded document context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=700
    )

    return response.choices[0].message.content.strip()


def _set_answer(state, answer):
    state["answer"] = clean_text(answer)
    return state


def generate_answer_from_state(state):
    question = state.get("question", "")
    docs = state.get("reranked_docs") or state.get("retrieved_docs") or []
    document_id = state.get("document_id")

    if is_greeting(question):
        if document_id:
            return _set_answer(
                state,
                "Hello 👋 Your document is ready. You can ask any question from the uploaded document."
            )

        return _set_answer(
            state,
            "Hello 👋 Please upload your document first, then ask me anything from it."
        )

    if not document_id:
        return _set_answer(
            state,
            "Please upload a document first, then ask a question."
        )

    if not docs:
        return _set_answer(state, FALLBACK_NOT_FOUND)

    context = get_context_from_docs(docs)

    if not context:
        return _set_answer(state, FALLBACK_NOT_FOUND)

    answer = generate_with_groq(question, context)

    sources = format_sources(docs)

    if (
        sources
        and FALLBACK_NOT_FOUND.lower() not in answer.lower()
        and "groq api key is missing" not in answer.lower()
    ):
        answer = answer + "\n\n" + sources

    return _set_answer(state, answer)