from utils.analyzer import analyze_resume

sample_resume = """
John Doe
Software Engineer

Responsible for managing a team and improving various processes.
Worked on backend systems for several years.
"""

result = analyze_resume(sample_resume)
import json
print(json.dumps(result, indent=2))