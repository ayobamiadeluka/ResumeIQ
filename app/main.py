from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from dotenv import load_dotenv
from app.ai_analyzer import ai_analyze_resume

import os
import uuid


load_dotenv()


app = FastAPI(title="ResumeIQ")


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


SKILLS = [
    "python",
    "javascript",
    "typescript",
    "java",
    "c++",
    "c#",
    "html",
    "css",
    "react",
    "node.js",
    "fastapi",
    "django",
    "flask",
    "sql",
    "mongodb",
    "git",
    "github",
    "docker",
    "aws",
    "azure",
    "machine learning",
    "artificial intelligence",
    "data analysis",
    "rest api",
    "linux",
    "figma",
]


REPORTS = {}


@app.get("/", response_class=HTMLResponse)
def home():

    with open(
        "templates/index.html",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    job_description: str = Form("")
):

    if not file.filename.lower().endswith(".pdf"):

        return {
            "error": "Please upload a PDF file."
        }


    os.makedirs(
        "uploads",
        exist_ok=True
    )


    safe_name = os.path.basename(
        file.filename
    )


    unique_name = (
        str(uuid.uuid4())[:8]
        + "_"
        + safe_name
    )


    file_path = os.path.join(
        "uploads",
        unique_name
    )


    with open(
        file_path,
        "wb"
    ) as buffer:

        buffer.write(
            await file.read()
        )


    reader = PdfReader(file_path)

    text = ""


    for page in reader.pages:

        text += page.extract_text() or ""


    text_lower = text.lower()

    job_lower = job_description.lower()


    # --------------------------------
    # Resume skill detection
    # --------------------------------

    detected = [
        skill
        for skill in SKILLS
        if skill in text_lower
    ]


    # --------------------------------
    # Job description skills
    # --------------------------------

    job_skills = [
        skill
        for skill in SKILLS
        if skill in job_lower
    ]


    matched = [
        skill
        for skill in job_skills
        if skill in text_lower
    ]


    missing = [
        skill
        for skill in job_skills
        if skill not in text_lower
    ]


    # --------------------------------
    # Job match calculation
    # --------------------------------

    if job_skills:

        match = round(
            len(matched)
            / len(job_skills)
            * 100
        )

    else:

        match = min(
            100,
            40 + len(detected) * 5
        )


    # --------------------------------
    # Resume quality
    # --------------------------------

    word_count = len(text.split())


    has_experience = (
        "experience" in text_lower
    )


    has_education = (
        "education" in text_lower
    )


    has_projects = (
        "projects" in text_lower
    )


    has_contact = (
        "@" in text
    )


    quality = 0


    quality += min(
        len(detected) * 4,
        25
    )


    quality += (
        20
        if has_experience
        else 0
    )


    quality += (
        20
        if has_education
        else 0
    )


    quality += (
        15
        if has_projects
        else 0
    )


    quality += (
        10
        if has_contact
        else 0
    )


    quality += (
        10
        if word_count >= 250
        else 0
    )


    quality = min(
        quality,
        100
    )


    score = round(
        (quality + match) / 2
    )


    # --------------------------------
    # Recommendations
    # --------------------------------

    recommendations = []


    if not has_contact:

        recommendations.append(
            "Add clear contact information."
        )


    if not has_experience:

        recommendations.append(
            "Add a professional experience section."
        )


    if not has_projects:

        recommendations.append(
            "Add projects that demonstrate practical skills."
        )


    if not has_education:

        recommendations.append(
            "Add your education background."
        )


    if missing:

        recommendations.append(
            "Consider adding relevant missing skills where you genuinely have them."
        )


    if word_count < 250:

        recommendations.append(
            "Add more measurable achievements and relevant details."
        )


    if not recommendations:

        recommendations.append(
            "Your resume has a strong basic structure. "
            "Focus on measurable achievements and tailoring it to each role."
        )


    # --------------------------------
    # Rating
    # --------------------------------

    if score >= 80:

        rating = "Strong"

    elif score >= 60:

        rating = "Good"

    elif score >= 40:

        rating = "Needs Improvement"

    else:

        rating = "Needs Major Improvement"


    # --------------------------------
    # Summary
    # --------------------------------

    summary = (
        f"Your resume received a {score}/100 overall score "
        f"and a {match}% job match. "
        f"ResumeIQ detected {len(detected)} relevant skills."
    )


    # --------------------------------
    # REAL AI ANALYSIS
    # --------------------------------

    ai_result = ai_analyze_resume(
        text,
        job_description
    )


    # --------------------------------
    # Store report
    # --------------------------------

    report_id = str(uuid.uuid4())


    REPORTS[report_id] = {

        "filename": safe_name,

        "score": score,

        "match": match,

        "word_count": word_count,

        "skills": detected,

        "matched": matched,

        "missing": missing,

        "recommendations": recommendations,

        "rating": rating,

        "summary": summary,

        "ai": ai_result

    }


    # --------------------------------
    # Return results
    # --------------------------------

    return {

        "report_id": report_id,

        "filename": safe_name,

        "score": score,

        "match": match,

        "word_count": word_count,

        "skills": detected,

        "matched": matched,

        "missing": missing,

        "recommendations": recommendations,

        "rating": rating,

        "summary": summary,

        "ai": ai_result

    }


# ========================================
# DOWNLOAD REPORT
# ========================================

@app.get("/download-report/{report_id}")
def download_report(report_id: str):

    report = REPORTS.get(report_id)


    if not report:

        return {
            "error": "Report not found."
        }


    os.makedirs(
        "reports",
        exist_ok=True
    )


    filename = (
        "ResumeIQ_Report_"
        + report_id[:8]
        + ".pdf"
    )


    path = os.path.join(
        "reports",
        filename
    )


    pdf = canvas.Canvas(
        path,
        pagesize=A4
    )


    width, height = A4

    y = height - 60


    # --------------------------------
    # Header
    # --------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        24
    )


    pdf.drawString(
        50,
        y,
        "ResumeIQ"
    )


    y -= 35


    pdf.setFont(
        "Helvetica",
        12
    )


    pdf.drawString(
        50,
        y,
        "Resume Analysis Report"
    )


    y -= 40


    # --------------------------------
    # Score
    # --------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        16
    )


    pdf.drawString(
        50,
        y,
        f"Overall Score: {report['score']}/100"
    )


    y -= 25


    pdf.setFont(
        "Helvetica",
        12
    )


    pdf.drawString(
        50,
        y,
        f"Job Match: {report['match']}%"
    )


    y -= 20


    pdf.drawString(
        50,
        y,
        f"Resume Words: {report['word_count']}"
    )


    y -= 40


    # --------------------------------
    # Skills
    # --------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        14
    )


    pdf.drawString(
        50,
        y,
        "Skills Detected"
    )


    y -= 22


    pdf.setFont(
        "Helvetica",
        11
    )


    skills_text = ", ".join(
        report["skills"]
    ) or "None detected"


    pdf.drawString(
        50,
        y,
        skills_text[:100]
    )


    y -= 40


    # --------------------------------
    # Missing skills
    # --------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        14
    )


    pdf.drawString(
        50,
        y,
        "Missing Skills"
    )


    y -= 22


    pdf.setFont(
        "Helvetica",
        11
    )


    missing_text = ", ".join(
        report["missing"]
    ) or "None detected"


    pdf.drawString(
        50,
        y,
        missing_text[:100]
    )


    y -= 40


    # --------------------------------
    # Recommendations
    # --------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        14
    )


    pdf.drawString(
        50,
        y,
        "Recommendations"
    )


    y -= 22


    pdf.setFont(
        "Helvetica",
        11
    )


    for recommendation in report[
        "recommendations"
    ]:

        if y < 70:

            pdf.showPage()

            y = height - 60

            pdf.setFont(
                "Helvetica",
                11
            )


        pdf.drawString(
            60,
            y,
            "- " + recommendation
        )


        y -= 20


    # --------------------------------
    # AI Analysis
    # --------------------------------

    ai_data = report.get("ai", {})


    if ai_data.get("available"):

        analysis = ai_data.get(
            "analysis",
            {}
        )


        if y < 180:

            pdf.showPage()

            y = height - 60


        pdf.setFont(
            "Helvetica-Bold",
            14
        )


        pdf.drawString(
            50,
            y,
            "AI Analysis"
        )


        y -= 25


        pdf.setFont(
            "Helvetica",
            10
        )


        ai_summary = analysis.get(
            "summary",
            ""
        )


        if ai_summary:

            pdf.drawString(
                50,
                y,
                "AI Summary:"
            )


            y -= 18


            # Break long summary into lines

            words = ai_summary.split()

            line = ""


            for word in words:

                test_line = (
                    line + " " + word
                ).strip()


                if len(test_line) > 95:

                    pdf.drawString(
                        60,
                        y,
                        test_line
                    )


                    y -= 15

                    line = word

                else:

                    line = test_line


            if line:

                pdf.drawString(
                    60,
                    y,
                    line
                )


                y -= 25


    pdf.save()


    return FileResponse(
        path,
        media_type="application/pdf",
        filename=filename
    )