import os
import re
from datetime import datetime
from pypdf import PdfReader


def clean_text(text):
    text = text or ""
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text, chunk_size=900, overlap=120):
    text = clean_text(text)

    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 1 <= chunk_size:
            current = (current + "\n" + para).strip()
        else:
            if current:
                chunks.append(current)

            if len(para) > chunk_size:
                start = 0
                while start < len(para):
                    end = start + chunk_size
                    part = para[start:end].strip()
                    if part:
                        chunks.append(part)
                    start = end - overlap
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks


def extract_pdf(file_path, filename, document_id):
    reader = PdfReader(file_path)
    final_chunks = []
    timestamp = datetime.now().isoformat()

    for page_no, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = clean_text(text)

        if not text:
            continue

        page_chunks = chunk_text(text)

        for index, chunk in enumerate(page_chunks, start=1):
            final_chunks.append({
                "text": chunk,
                "metadata": {
                    "document_id": document_id,
                    "filename": filename,
                    "page": page_no,
                    "chunk": index,
                    "type": "pdf",
                    "timestamp": timestamp
                }
            })

    return final_chunks


def extract_text_file(file_path, filename, document_id):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    text = clean_text(text)
    final_chunks = []
    timestamp = datetime.now().isoformat()

    for index, chunk in enumerate(chunk_text(text), start=1):
        final_chunks.append({
            "text": chunk,
            "metadata": {
                "document_id": document_id,
                "filename": filename,
                "page": None,
                "chunk": index,
                "type": "text",
                "timestamp": timestamp
            }
        })

    return final_chunks


def process_document(file_path, filename, document_id):
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        return extract_pdf(file_path, filename, document_id)

    if ext in [".txt", ".md"]:
        return extract_text_file(file_path, filename, document_id)

    raise ValueError("Only PDF, TXT, and MD files are supported.")