import os
import json
from dotenv import load_dotenv
from google import genai
from utils.retriever import retrieve_examples

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are a precise, experienced hiring manager and resume editor.
You review resumes the way a sharp editor marks up a manuscript: specific, honest,
and useful — never generic filler like "add more action verbs."

You will be given the resume text, an optional job posting, and a set of REFERENCE
EXAMPLES of strong resume bullets. Use the reference examples only as a style/quality
bar for your rewrites — never copy them directly, always rewrite based on what's
actually in the candidate's resume.

Respond with ONLY a raw JSON object, no markdown fences, no preamble, matching this exact shape:
{
"overall_score": 0,
"verdict": "2-3 sentence overall impression, direct and specific to THIS resume",
"scores": {
"impact": 0,
"clarity": 0,
"formatting": 0,
"ats_fit": 0
},
  "strengths": ["specific strength 1", "specific strength 2"],
  "issues": [
    {
      "quote": "a short exact phrase copied from the resume (under 12 words)",
      "problem": "what's weak about it, specifically",
      "rewrite": "a concrete, better version of that line, in the quality style of the reference examples"
    }
  ],
  "ats_gaps": ["keyword or requirement missing from the resume, only if a job description was provided, else empty array"]
}

Scores are 0-10.

overall_score should be an integer from 0-100 representing the overall quality of the resume.

Give 3-5 strengths and 4-7 issues.

Quotes must be copied verbatim from the resume text.

Be specific and concrete, never vague."""

def analyze_resume(resume_text, job_description=None):
    # Retrieve reference examples based on the resume content itself
    reference_examples = retrieve_examples(resume_text, top_k=4)
    references_block = "\n".join(f"- {ex}" for ex in reference_examples)

    user_message = f"RESUME:\n{resume_text}"
    if job_description:
        user_message += f"\n\nTARGET ROLE / JOB POSTING:\n{job_description}"
    else:
        user_message += "\n\n(No job posting provided — review generally.)"

    user_message += f"\n\nREFERENCE EXAMPLES (style/quality bar for rewrites, do not copy directly):\n{references_block}"

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=user_message,
        config={"system_instruction": SYSTEM_PROMPT}
    )

    raw_text = response.text.strip()
    cleaned = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response", "raw": cleaned}