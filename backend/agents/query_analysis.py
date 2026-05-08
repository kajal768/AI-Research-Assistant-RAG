import re


def _clean_query(question):
    question = question or ""
    question = question.strip()
    question = re.sub(r"\s+", " ", question)
    return question


def _is_greeting(question):
    q = question.lower().strip()

    greetings = {
        "hello",
        "hi",
        "hey",
        "hii",
        "helo",
        "good morning",
        "good afternoon",
        "good evening",
        "namaste",
        "sat sri akal",
    }

    return q in greetings or q.startswith("hello ") or q.startswith("hi ")


def _is_summary_query(question):
    q = question.lower().strip()

    keywords = [
        "summary",
        "summarize",
        "what is mentioned",
        "what details",
        "details mentioned",
        "mentioned the detail",
        "mentioned details",
        "about document",
        "explain document",
        "document main kya",
        "document mein kya",
        "kya likha",
        "kya details",
        "overview",
    ]

    return any(keyword in q for keyword in keywords)


def _is_agent_count_query(question):
    q = question.lower().strip()

    return (
        "how many agents" in q
        or "number of agents" in q
        or "agents required" in q
        or "agent required" in q
        or "kitne agents" in q
    )


def _is_document_name_query(question):
    q = question.lower().strip()

    return (
        "document name" in q
        or "file name" in q
        or "filename" in q
        or "name of document" in q
        or "name of this document" in q
    )


def analyze_query(state):
    question = state.get("question", "")
    clean_question = _clean_query(question)

    query_type = "specific"

    if _is_greeting(clean_question):
        query_type = "greeting"
    elif _is_agent_count_query(clean_question):
        query_type = "agent_count"
    elif _is_document_name_query(clean_question):
        query_type = "document_name"
    elif _is_summary_query(clean_question):
        query_type = "summary"

    state["analyzed_query"] = {
        "original_question": question,
        "clean_query": clean_question.lower(),
        "query_type": query_type,
        "needs_web_search": False
    }

    return state