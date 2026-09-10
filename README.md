# Policy Reader — Insurance Policy Comparator & Claim Helper

A RAG-based assistant that reads your actual insurance policy PDFs (not marketing
pages) and answers questions grounded in the fine print — with citations to the
exact clause and page it came from. Upload 2–3 policies to compare them side by
side on any question ("which one covers maternity better?", "why might my claim
get rejected?").

## Why this exists

People buy health/term insurance without understanding exclusions, then get
denied claims they didn't expect. This tool retrieves answers directly from the
policy documents themselves, so every answer is traceable back to a real clause
instead of generic advice.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │─────▶│   FastAPI     │─────▶│  ChromaDB   │
│  (Vite) UI  │◀─────│   Backend     │◀─────│  (vectors)  │
└─────────────┘      └──────┬───────┘      └─────────────┘
                             │
                      ┌──────▼───────┐
                      │  Gemini API   │
                      │ (embed + gen) │
                      └──────────────┘
```

- **PDF parsing**: PyMuPDF extracts text per page; a clause-aware chunker splits
  on numbered sections ("4.2 Exclusions") where possible, falling back to a
  sliding window otherwise — better retrieval than naive fixed-size chunking on
  legal documents.
- **Embeddings + generation**: Gemini free tier (`text-embedding-004` for
  embeddings, `gemini-1.5-flash` for answers).
- **Vector store**: ChromaDB (persistent, local/self-hosted — no external vector
  DB account needed).
- **Grounding**: every answer is generated only from retrieved chunks, with a
  system prompt that instructs the model to say "not specified" rather than
  guess, and the UI shows the exact source excerpt per answer.

## Tech stack

| Layer | Tech |
|---|---|
| Backend | FastAPI, Python 3.11 |
| Frontend | React + Vite |
| Vector DB | ChromaDB |
| LLM | Google Gemini (free tier) |
| PDF parsing | PyMuPDF |
| Containerization | Docker, docker-compose |
| CI | GitHub Actions |
| Deployment | Render (backend) + Vercel (frontend) |

## Local development

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # then paste your Gemini API key into .env
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`. Interactive API docs at
`http://localhost:8000/docs`.

Get a free Gemini API key at https://aistudio.google.com/apikey.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env       # VITE_API_URL=http://localhost:8000
npm run dev
```

Frontend runs at `http://localhost:5173`.

### 3. Or run everything with Docker Compose

```bash
export GEMINI_API_KEY=your_key_here
docker compose up --build
```

## Deployment (free tier)

### Backend → Render

1. Push this repo to GitHub.
2. On [render.com](https://render.com), New → Web Service → connect your repo.
3. Root directory: `backend`. Build via Dockerfile (Render auto-detects it).
4. Add environment variable `GEMINI_API_KEY` with your key.
5. Add environment variable `CORS_ORIGINS` = your Vercel URL once you have it
   (comma-separated if multiple).
6. Deploy. Note the live URL, e.g. `https://policy-reader-api.onrender.com`.

### Frontend → Vercel

1. On [vercel.com](https://vercel.com), New Project → import the same repo.
2. Root directory: `frontend`. Framework preset: Vite (auto-detected).
3. Add environment variable `VITE_API_URL` = your Render backend URL.
4. Deploy. Note the live URL, e.g. `https://policy-reader.vercel.app`.
5. Go back to Render and update `CORS_ORIGINS` to this Vercel URL, then redeploy
   the backend so it accepts requests from the frontend.

Render's free tier spins down after inactivity, so the first request after a
while can take ~30–50 seconds to wake up — worth mentioning in a demo/interview
so it doesn't look broken.

## Project structure

```
insurance-rag-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app + routes
│   │   ├── config.py         # settings from env
│   │   ├── pdf_parser.py     # PyMuPDF extraction + clause chunking
│   │   ├── gemini_client.py  # embeddings + generation calls
│   │   ├── vectorstore.py    # ChromaDB wrapper
│   │   ├── rag.py            # retrieval + grounded answer/compare logic
│   │   ├── models.py         # Pydantic schemas
│   │   └── routers/          # upload / query / compare endpoints
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── components/
│   └── package.json
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Sample data for demo

Don't upload real personal policies to the public demo. Use publicly available
sample policy wordings — most Indian insurers (e.g. Star Health, HDFC Ergo, ICICI
Lombard) publish sample policy PDFs on their websites for exactly this purpose.

## Limitations

- Answers are only as good as the retrieved chunks — very unusual PDF layouts
  (scanned images, multi-column tables) may need OCR, which isn't included yet.
- This is not legal or financial advice — always confirm with the insurer
  directly before relying on an answer for a real claim decision.
