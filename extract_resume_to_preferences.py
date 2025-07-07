import json
import re
from PyPDF2 import PdfReader

# Paths
RESUME_PATH = "Resume.pdf"
PREFERENCES_PATH = "job_preferences.json"

# Helper: Extract text from PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Helper: Parse fields from resume text
def parse_resume_fields(text):
    fields = {}
    # Name (look for 'Jason James' or similar)
    name_match = re.search(r"(?i)([A-Z][a-z]+) ([A-Z][a-z]+)", text)
    if name_match:
        fields["name"] = name_match.group(1)
        fields["surname"] = name_match.group(2)
    # Email
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    if email_match:
        fields["email"] = email_match.group(0)
    # Phone
    phone_match = re.search(r"(\+?\d[\d\s\-\(\)]{7,})", text)
    if phone_match:
        fields["phone"] = phone_match.group(0)
    # City, Country
    city_match = re.search(r"City\s*\n([A-Za-z\s]+)", text)
    if city_match:
        fields["city"] = city_match.group(1).strip()
    country_match = re.search(r"Country\s*\n([A-Za-z\s]+)", text)
    if country_match:
        fields["country"] = country_match.group(1).strip()
    # LinkedIn
    linkedin_match = re.search(r"linkedin\.com/in/[\w\-]+", text)
    if linkedin_match:
        fields["linkedin"] = linkedin_match.group(0)
    # Github
    github_match = re.search(r"github\.com/[\w\-]+", text)
    if github_match:
        fields["github"] = github_match.group(0)
    # Wanted Job Title
    job_title_match = re.search(r"Wanted Job Title\s*\n([A-Za-z\s]+)", text)
    if job_title_match:
        fields["wanted_job_title"] = job_title_match.group(1).strip()
    # Skills (look for a long comma-separated list)
    skills_match = re.search(r"(?i)(skills|abilities|technologies|proficiencies)[^\n]*\n([\w\s,\-\./]+)", text)
    if skills_match:
        skills = [s.strip() for s in skills_match.group(2).split(",") if s.strip()]
        fields["skills"] = skills
    return fields

# Helper: Update job_preferences.json
def update_preferences(fields):
    with open(PREFERENCES_PATH, "r", encoding="utf-8") as f:
        prefs = json.load(f)
    # Personal Information
    pi = prefs.get("personal_information", {})
    pi["name"] = fields.get("name", pi.get("name", ""))
    pi["surname"] = fields.get("surname", pi.get("surname", ""))
    pi["email"] = fields.get("email", pi.get("email", ""))
    pi["phone"] = fields.get("phone", pi.get("phone", ""))
    pi["city"] = fields.get("city", pi.get("city", ""))
    pi["country"] = fields.get("country", pi.get("country", ""))
    pi["linkedin"] = fields.get("linkedin", pi.get("linkedin", ""))
    pi["github"] = fields.get("github", pi.get("github", ""))
    prefs["personal_information"] = pi
    # Job Title
    if "wanted_job_title" in fields:
        prefs["keywords"] = [fields["wanted_job_title"]] + prefs.get("keywords", [])
    # Skills
    if "skills" in fields:
        prefs["skills_required"] = list(set(prefs.get("skills_required", []) + fields["skills"]))
    with open(PREFERENCES_PATH, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=2, ensure_ascii=False)
    print("job_preferences.json updated with extracted resume info.")

if __name__ == "__main__":
    text = extract_text_from_pdf(RESUME_PATH)
    fields = parse_resume_fields(text)
    update_preferences(fields) 