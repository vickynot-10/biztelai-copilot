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
LLM_MODEL=gemini-3.1-flash-lite
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

Model names change over time. If you get a 404, test which models your key can actually call and use one that works.

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

When the answer is not in the documents, the API returns `found: false` with an empty `answer` and no sources, and the UI shows "Not in the documents".

## Results for the 5 assignment sample questions

Each answer below was checked against the source passage the app returned.

### 1. What is the recommended coolant concentration for the TX-200 CNC turning centre?

**Answer:** The recommended coolant concentration for the TX-200 CNC turning centre is 6 - 8 %.

- Source: MNT-MAN-CNC-02 Rev 02, section 3 "Normal Operating Parameters", page 1
- Safety critical: no. Version notes: none.

### 2. The machine is showing alarm AL-104. What does it mean and what should the operator do?

**Answer:** AL-104 means the way lube oil level is low. The operator should top up with ISO VG 68 oil to the MAX mark, then press RESET. The machine can continue after reset.

- Source: MNT-MAN-CNC-02 Rev 02, section 6 "Common Alarms", pages 1 to 2
- Safety critical: no. Version notes: none.

### 3. Who is allowed to remove a lockout lock from a machine?

**Answer:** Each authorised person removes only their own lock. Nobody may remove another person's lock. If an authorised person has left the plant without removing their lock, the lock may be removed only through this procedure:

1. The Shift Supervisor makes every reasonable effort to contact the lock owner by phone.
2. If the owner cannot be reached, the Production Manager and the Safety Officer must both authorise removal.
3. The machine is physically inspected to confirm it is safe to re-energise.
4. The removal is recorded on form SF-12 Lock Removal Record.
5. The lock owner must be informed before they resume work on their next shift.

- Sources: SAF-SOP-003 Rev 05, section 5 "Removing Locks" and section 6 "Removal of a Lock When the Owner Is Absent"
- Safety critical: **yes** (the UI shows a "Safety step" warning). Version notes: none.

### 4. What is the outer diameter tolerance for the BH-220 bearing housing?

**Answer:** The outer diameter tolerance for the BH-220 bearing housing is +/- 0.050 (mm, nominal 90.000, checked with a digital caliper, class Major).

- Source: QC-SOP-014 Rev 04, section 6 "Inspection Dimensions - BH-220 Bearing Housing", page 2
- Version note: "QC-SOP-014: this answer is from Rev 04 (effective 01-Jul-2026). Rev 03 is superseded, so don't follow old printed copies."

### 5. How often should spindle runout be checked, and who does it?

**Answer:** Spindle runout should be checked monthly by a maintenance technician.

- Source shown: MNT-MAN-CNC-02 Rev 02, section 3 "Normal Operating Parameters", page 1 (spindle runout limit 0.005 mm max., dial indicator)
- Known issue: the passage shown only gives the limit and the check method. The "monthly" and "maintenance technician" details must come from the PM schedule in the same manual, which the app did not list as a source. See "Known limitations".

## My own test questions

### A lot of 120 pieces has one minor defect. Accept or reject?

**Answer:** The lot must be rejected. For a lot size of 120 pieces, the sampling plan requires 13 samples to be inspected. According to the table in QC-SOP-014 Rev 04, the lot is rejected if there is 1 or more minor defects.

- Source: QC-SOP-014 Rev 04, section 4 "Sampling Plan", page 1
- Version note: Rev 03 is superseded.
- Note: the rule applies to defects found in the 13 inspected samples, not to the whole lot. The question did not say which, and the answer did not point that out.

### What is the maximum spindle speed of the TX-200? (not in the documents)

**Result:** not found. The UI shows "Not in the documents". Raw response:

```json
{
  "found": false,
  "answer": "",
  "sources": [],
  "safety_critical": false,
  "version_notes": []
}
```

### What PPE is required when applying a lockout lock? (not in the documents)

**Result:** not found, with the same raw response as above. The search found loosely related lockout text, so it was the LLM that decided the answer was not there.

## Known limitations

- Source lists can include passages that were not needed (for example, question 1 also lists the alarms table and the Purpose section), and sometimes a source is missing (question 5).
- Retrieval is tuned on four documents. A larger document set would need re-tuning and proper evaluation.
- The LLM can sound more certain than the question allows (see the 120-piece lot question).
- Answers take a few seconds because of the hosted LLM call.
- No login and no per-user history.

See `THINKING.md` for the user analysis, user journey, AI challenge, the improvement and why it was chosen, and the final reflection.
