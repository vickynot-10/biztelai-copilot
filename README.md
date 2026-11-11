# BiztelAI Shop-Floor Copilot

A simple RAG app for manufacturing supervisors. A supervisor asks a question (from a laptop, phone or tablet) and gets an answer **only from the plant's SOPs and manuals**, with the source document, revision, section and page shown. If the answer is not in the documents, the app says so instead of guessing.

## Features

- Answers grounded in the provided PDFs, with the exact source passage and a link to the PDF page
- Clear **"Not in the documents"** response when nothing relevant is found (two safeguards: a search score filter, then the LLM's own judgement)
- **Improvement added:** version awareness and a safety flag
  - If the answer comes from a document that has a newer or older revision, a version note says which revision was used and that the other one is superseded (QC-SOP-014 Rev 04 replaces Rev 03)
  - Lockout/tagout and energy-isolation answers are flagged as **safety critical**, telling the person to confirm with the Safety Officer or shift supervisor
- Mobile-friendly UI with sample questions, a Back button, and suggested questions below each answer
- Runs on the local network so it can be opened from a phone

## Tech stack

- **Backend:** FastAPI, PyMuPDF (PDF parsing), sentence-transformers (embeddings and retrieval), NumPy
- **LLM:** Gemini through its OpenAI-compatible endpoint (`openai` Python SDK)
- **Frontend:** React, TypeScript, Vite, Tailwind, shadcn/ui

## Project structure

```
├── backend
│   ├── data/            # the four source PDFs
│   ├── routes/          # ask.py, health.py
│   ├── samples/         # Sample_Questions.pdf
│   ├── schemas/         # request/response models
│   ├── services/        # ingest.py, retrieval.py, llm.py, ask_service.py
│   ├── main.py
│   └── requirements.txt
└── ui
    ├── src/             # App.tsx, components, styles
    ├── package.json
    └── vite.config.ts
```

## Setup and run

### Prerequisites

- Python 3.10+
- Node.js 18+
- A Gemini API key (from Google AI Studio)

### 1. Build the UI

```powershell
cd ui
npm install
npm run build
```

### 2. Set up the backend

```powershell
cd ..\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`requirements.txt`:

```
fastapi>=0.110
uvicorn[standard]>=0.29
pymupdf>=1.24
sentence-transformers>=2.7
numpy>=1.26
openai>=1.30
python-dotenv>=1.0
```

### 3. Add your environment variables

Create a file named `.env` inside `backend/` (the API key is intentionally left empty here):

```env
LLM_API_KEY=
LLM_MODEL=gemini-3.8-flash
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

### 4. Start the server

From the `backend` folder, with the virtual environment active:

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/ on the laptop.

## API

`POST /api/ask`

```json
{ "question": "A lot of 120 pieces has one minor defect. Accept or reject?" }
```

Response fields: `found`, `answer`, `sources[]`, `safety_critical`, `version_notes[]`.
