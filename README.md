

# Environment Variables

Create a `.env` file inside the `backend/` folder.

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama3-8b-8192
FRONTEND_URL=http://127.0.0.1:5500
```

If using OpenAI instead of Groq:

```env
OPENAI_API_KEY=your_openai_api_key
```

Do not commit actual API keys to GitHub.

---

# Backend Setup

Clone the repository:

```bash
git clone https://github.com/kajal768/AI-Research-Assistant-RAG.git
```

Move into project folder:

```bash
cd AI-Research-Assistant-RAG/backend
```

Create virtual environment:

```bash
python -m venv venv
```

Activate virtual environment:

```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run backend server:

```bash
uvicorn main:app --reload
```

Backend runs on:

```bash
http://127.0.0.1:8000
```

Swagger API Documentation:

```bash
http://127.0.0.1:8000/docs
```

---

# Frontend Setup

Move to frontend folder:

```bash
cd ../frontend
```

Run local frontend server:

```bash
python -m http.server 5500
```

Frontend URL:

```bash
http://127.0.0.1:5500
```

Update backend API URL inside `app.js` if needed.

---

# API Endpoints

| Method | Endpoint | Description |
|------|-----------|-------------|
| POST | `/upload` | Upload documents |
| POST | `/chat` | Ask questions |
| GET | `/history` | Retrieve conversation history |
| GET | `/docs` | Swagger API documentation |

---

# How It Works

1. User uploads PDF, TXT, or Markdown files.
2. Documents are processed and chunked.
3. Chunks are converted into embeddings.
4. Vector database stores embeddings.
5. User asks questions.
6. LangGraph agents coordinate retrieval and response generation.
7. AI generates contextual answers with citations.

---

# Deployment

## Backend Deployment (Render)

Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Add environment variables inside Render dashboard.

---

## Frontend Deployment (Vercel)

Deploy the `frontend/` folder on Vercel.

Update API base URL inside `app.js` with deployed backend URL.

---

# Important Notes

- Do not upload `.env` file to GitHub.
- Add `.env` inside `.gitignore`.
- Uploaded files are stored temporarily.
- Vector database stores processed document embeddings.
- The project currently uses semantic vector retrieval for document Q&A.

---

# Author

Kajal  
