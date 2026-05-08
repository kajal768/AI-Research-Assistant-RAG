conversation_history = []


def add_to_history(question, answer, citations=None):
    conversation_history.append({
        "question": question,
        "answer": answer,
        "citations": citations or []
    })


def get_history():
    return conversation_history


def get_recent_context(limit=3):
    recent = conversation_history[-limit:]

    context = ""

    for item in recent:
        context += f"User: {item['question']}\n"
        context += f"Assistant: {item['answer']}\n\n"

    return context.strip()


def clear_history():
    conversation_history.clear()
    return True