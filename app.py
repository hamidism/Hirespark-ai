import os
import json
from flask import Flask, render_template, request, Response
from utils.parser import extract_resume_text
from utils.analyzer import analyze_resume

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    result = None
    error = None
    extracted_text = None

    if request.method == "POST":
        file = request.files.get("resume")
        job_description = request.form.get("job_description", "").strip()

        if not file or not file.filename:
            error = "Please select a file."
        else:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)
            try:
                extracted_text = extract_resume_text(file_path)
                if not extracted_text or len(extracted_text.strip()) < 30:
                    error = "Couldn't extract enough text from that file. It may be scanned/image-based, or empty. Try a different resume."
                else:
                    result = analyze_resume(extracted_text, job_description or None)
                    if "error" in result:
                        error = "The AI response couldn't be parsed. Please try again."
                        result = None
            except ValueError as e:
                error = str(e)
            except Exception as e:
                error = "Something went wrong while analyzing your resume. Please try again in a moment."
                print(f"[ERROR] {e}")

    return render_template("index.html", result=result, error=error)
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
@app.route("/export", methods=["POST"])
def export():
    result_json = request.form.get("result_data")
    if not result_json:
        return "No data to export", 400

    result = json.loads(result_json)

    report = f"""HIRESPARK — RESUME FEEDBACK REPORT
{'='*50}

VERDICT
{result.get('verdict', '')}

SCORES
"""
    for key, val in result.get("scores", {}).items():
        report += f"- {key.capitalize()}: {val}/10\n"

    report += "\nSTRENGTHS\n"
    for s in result.get("strengths", []):
        report += f"- {s}\n"

    report += "\nLINE NOTES\n"
    for issue in result.get("issues", []):
        report += f"\nOriginal: \"{issue.get('quote','')}\"\n"
        report += f"Issue: {issue.get('problem','')}\n"
        report += f"Rewrite: {issue.get('rewrite','')}\n"

    if result.get("ats_gaps"):
        report += "\nMISSING FROM JOB POSTING\n"
        for gap in result["ats_gaps"]:
            report += f"- {gap}\n"

    return Response(
        report,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=hirespark_report.txt"}
    )
@app.route("/debug-files")
def debug_files():
    base = os.path.dirname(os.path.abspath(__file__))
    listing = {}
    for root, dirs, files in os.walk(base):
        if "_vendor" in root or ".git" in root:
            continue
        rel = os.path.relpath(root, base)
        listing[rel] = files
    return {"base_dir": base, "contents": listing}
if __name__ == "__main__":
    app.run(debug=True)
