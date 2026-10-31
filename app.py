from flask import Flask,render_template,request
from PyPDF2 import PdfReader
import re
import os
from werkzeug.utils import secure_filename
from sentence_transformers import SentenceTransformer, util
from docx import Document

skills_list = [
    # =========================
    # PRODUCTION
    # =========================
    "Production Planning",
    "Production Monitoring",
    "Production Control",
    "Production Engineering",
    "Production Scheduling",

    # =========================
    # MANUFACTURING
    # =========================
    "Injection Molding",
    "Blow Molding",
    "Plastic Manufacturing",
    "Manufacturing",
    "Process Control",
    "Process Improvement",
    "Process Optimization",
    "Troubleshooting",

    # =========================
    # MAINTENANCE
    # =========================
    "Preventive Maintenance",
    "Maintenance Operations",
    "Equipment Maintenance",

    # =========================
    # QUALITY
    # =========================
    "Root Cause Analysis",
    "Root Cause Failure Analysis",
    "RCFA",
    "Corrective Actions",
    "Quality Management",

    # =========================
    # PRODUCTIVITY
    # =========================
    "OEE",
    "Overall Equipment Effectiveness",
    "Takt Time",
    "Cycle Time",
    "Cycle Time Reduction",
    "Yield Improvement",

    # =========================
    # MANUFACTURING SYSTEMS
    # =========================
    "5S",
    "Kaizen",
    "TPM",
    "Jigs",
    "Fixtures",

    # =========================
    # MANAGEMENT
    # =========================
    "Manpower Management",
    "Vendor Management",
    "Inventory Management",
    "Resource Management",

    # =========================
    # ERP / SOFTWARE
    # =========================
    "ERP",
    "TranZact",
    "AutoCAD",
    "Excel",
    "Bill of Materials",
    "BOM",

    # =========================
    # STANDARDS
    # =========================
    "ISO 16949",
    "IATF 16949",

    # =========================
    # DOCUMENTATION
    # =========================
    "SOP",
    "Standard Operating Procedures",
    "Audit Documentation",

    # =========================
    # PROGRAMMING / IT
    # =========================
    "Python",
    "Java",
    "C++",
    "SQL",
    "Flask",
    "Django",
    "HTML",
    "CSS",
    "JavaScript",

    # =========================
    # DATA / AI
    # =========================
    "Machine Learning",
    "Deep Learning",
    "Data Science",
    "Data Analysis",
    "Pandas",
    "NumPy",
    "TensorFlow",
    "PyTorch",

    # =========================
    # WEB DEVELOPMENT
    # =========================
    "Git",
    "GitHub",
    "React",
    "Node.js",
    "MongoDB",
    "MySQL"
]

education_keywords = [
    "education",
    "bachelor",
    "b.tech",
    "b.e",
    "be",
    "bsc",
    "bca",
    "b.com",
    "master",
    "m.tech",
    "m.e",
    "msc",
    "mba",
    "mca",
    "collage",
    "diploma",
    "degree",
    "university",
    "school",
    "12th",
    "10th",
    "hsc",
    "ssc" 
]

experience_keywords = [
            "experience",
            "work experience",
            "internship",
            "intern",
            "software developer",
            "developer",
            "software engineer",
            "engineer",
            "professional experience",
            "job experience",
            "employment history",
            "career history",
            "projects",
            "analyst"
]

model = SentenceTransformer("all-MiniLM-L6-v2")

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route('/', methods=['GET',
'POST'])
def home():
    text = ""
    text_lower = ""
    name = ""
    email = ""
    phone = ""
    skills = []
    education = []
    experience = []
    job_description = ""
    matched_skills = []
    missing_skills = []
    ats_score = 0
    ai_match_score = 0
    suggestions =[]

    if request.method == 'POST':

        file = request.files.get('resume')
        job_description = request.form.get("job_description", '').strip()   
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

        if file.filename.lower().endswith(".pdf"):

                reader = PdfReader(file_path)

                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"

        elif file.filename.lower().endswith(".docx"):

                document = Document(file_path)

                for paragraph in document.paragraphs:
                        if paragraph.text:
                            text +=  paragraph.text + "\n"
        else:
            return render_template(
                    "index.html",
                    suggestions="Please upload a PDF or DOCX resume."
             ) 

        text_lower = text.lower()
        lines =  text.splitlines()                    


        if job_description:
                  resume_embedding = model.encode(text,convert_to_tensor=True)
                  job_embedding = model.encode(job_description,convert_to_tensor=True)

                  similarity = util.cos_sim(resume_embedding,job_embedding).item()
                  ai_match_score = round(similarity * 100, 2)  

                  print("AI MATCH SCORE:", ai_match_score)
        else:
                  ai_match_score = 0  

        print("TEXT LENGTH:", len(text))
        print("TEXT PREVIEW:", text[:500] )  
        skillls = []           

        text_lower = text.lower()
        
        for skill in skills_list:
            if skill.lower() in text_lower:
                if skill not in skills:
                    skills.append(skill)
        
        print ("SKILLS", skills)          

        lines = [
                line.strip()
                for line in text.splitlines()
                if line.strip()
            ]

        if lines:
                name = lines[0]        

        email = re.findall(r'\S+@\S+', text)
        phone = re.findall(
            r'(?:\+91[\s-]?)?\d[\d\s-]{8,}\d',
            text
        )


    education = []

    lines = text.splitlines()

    for line in lines:

            line_lower = line.lower()

            for education_item in education_keywords:

                if education_item.lower() in line_lower:

                    if line not in education:

                        education.append(line)

                    break


    print("EDUCATION:", education)

    found_experience = []

    for experience_item in experience_keywords:

        if experience_item.lower() in text_lower:

            if experience_item not in found_experience:

                found_experience.append(experience_item)

    experience = found_experience

    print("EXPERIENCE:", experience)

    # -------------------------
# JOB SKILLS
# -------------------------

    job_skills = [
    skill
    for skill in skills_list
    if skill.lower() in job_description.lower()
    ]

# -------------------------
# MATCHED SKILLS
# -------------------------

    matched_skills = [
    skill
    for skill in skills
    if skill.lower() in job_description.lower()
    ]

# -------------------------
# MISSING SKILLS
# -------------------------

    missing_skills = [
    skill
    for skill in job_skills
    if skill not in matched_skills
    ]

# -------------------------
# KEYWORD SCORE
# -------------------------

    if job_skills:

        keyword_score = round(
        (len(matched_skills) / len(job_skills)) * 100
    )

    else:

        keyword_score = 0


# -------------------------
# ATS SCORE
# -------------------------

    if job_description:

        ats_score = round(
        (keyword_score * 0.6) +
        (ai_match_score * 0.4)
    )

    else:

        ats_score = 0


# -------------------------
# SUGGESTIONS
# -------------------------

    suggestions = []

    if missing_skills:

        suggestions.append(
        "Consider adding these missing skills if you have experience with them: "
        + ", ".join(missing_skills)
    )

    if ats_score < 50:

        suggestions.append(
        "Your ATS score is low. Try adding more skills that match the job description."
    )

    elif ats_score < 80:

     suggestions.append(
        "Your ATS score is moderate. Try highlighting more relevant skills and experience."
    )

    else:

        suggestions.append(
        "Your resume has a strong match with the job description."
    )



    education = []

    for line in lines:

                line_lower = line.lower()

                if any(
                    keyword in line_lower
                    for keyword in education_keywords
                ):

                    if line not in education:
                        education.append(line)

    experience = []

    experience_match = re.search(
    r'(?:WORK EXPERIENCE|PROFESSIONAL EXPERIENCE)'
    r'\s*:?\s*'
    r'(.*?)'
    r'(?=\b(?:ACADEMIC QUALIFICATIONS|EDUCATION|PERSONAL DETAILS|DECLARATION)\b|$)',
    text,
    re.IGNORECASE | re.DOTALL
)

    if experience_match:
            experience_text = experience_match.group(1).strip()

            
            company_pattern = re.compile(
                r'\b[A-Z][A-Z\s&.]+'
                r'(?:PVT\.?\s*LTD\.?|PRIVATE LIMITED|LTD\.?|LIMITED)\b',
                re.IGNORECASE
    )

            jobs = company_pattern.split(experience_text)

            for job in jobs:
                job = job.strip()
                if job:
                    experience.append(job)

        # DEBUG OUTPUT
    print("\n========== NAME ==========")
    print(name)
    print("\n========== EMAIL ==========")
    print(email)
    print("\n========== PHONE ==========")
    print(phone)
    print("\n========== SKILLS ==========")
    print(skills)
    print("\n========== EDUCATION ==========")
    print(education)
    print("\n========== EXPERIENCE ==========")
    print(experience)

    return render_template(
        'index.html',
        text=text,
        name=name,
        email=email,
        phone=phone,
        skills=skills,
        education=education,
        experience=experience,
        job_description=job_description,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        ats_score=ats_score,
        ai_match_score=ai_match_score,
        suggestions=suggestions
)

if __name__ == '__main__':
    app.run(debug=False)