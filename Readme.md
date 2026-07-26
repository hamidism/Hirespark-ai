# HireSpark

An AI-powered resume feedback tool that gives job seekers specific, line-by-line
editing suggestions — not generic advice like "add more action verbs."

## The Problem

Most resume advice online is generic and impersonal. Job seekers either get vague
tips or expensive human reviews. HireSpark gives a fast, specific, line-by-line
critique of an actual resume, grounded in what strong resumes really look like.

## Approach

1. User uploads a resume (PDF/DOCX) and optionally pastes a target job description.
2. The app extracts the raw text from the file.
3. A small local corpus of strong resume bullet examples is searched (keyword-overlap
   retrieval) to find style/quality references relevant to the resume's content.
4. The resume text, job description, and retrieved examples are sent to Gemini with a
   structured prompt that forces a strict JSON response: an overall verdict, 0-10
   scores across 4 categories, strengths, line-by-line issues (each tied to an exact
   quote from the resume with a problem and a rewrite), and ATS keyword gaps.
5. Results are rendered in a clean web UI, with an option to download a text report.

## Tech Stack

- **Backend:** Flask (Python)
- **AI:** Google Gemini API (`gemini-flash-latest`)
- **File parsing:** pdfplumber (PDF), python-docx (DOCX)
- **Retrieval:** lightweight keyword-overlap search over a local JSON corpus of
  strong resume bullets (no external vector DB — kept intentionally simple)
- **Frontend:** Flask templates (Jinja2) + vanilla HTML/CSS/JS

## Structured Output

The AI is prompted to return only a JSON object matching a fixed schema (verdict,
scores, strengths, issues, ats_gaps). This makes the output directly renderable in
the UI without further parsing logic, and keeps responses consistent across runs.

## Retrieval (RAG-lite)

Before calling the AI, the app retrieves the most relevant example bullets from a
local corpus (leadership, impact/metrics, technical, process improvement, sales,
communication) based on keyword overlap with the resume text. These are passed to
the model as a style reference, so rewrite suggestions read like realistic strong
resume bullets rather than generic AI phrasing.

## What I'd Improve With More Time

- Replace keyword-overlap retrieval with proper embeddings for more accurate
  example matching
- Handle scanned/image-based PDFs with OCR
- Add resume history / before-and-after comparison for a single user
- Export as a formatted PDF instead of plain text
- Add authentication so users can save past reviews
- Better handling of multi-column/table-based resume layouts during text extraction

## Running Locally

1. `python -m venv venv` and activate it
2. `pip install -r requirements.txt`
3. Add your Gemini API key to a `.env` file: `GEMINI_API_KEY=your_key_here`
4. `python app.py`
5. Open `http://127.0.0.1:5000`