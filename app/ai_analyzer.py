import os
import json

from groq import Groq


def ai_analyze_resume(resume_text, job_description):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return {
            "available": False,
            "message": "AI analysis is not configured yet."
        }

    client = Groq(
        api_key=api_key
    )

    prompt = f"""
You are ResumeIQ, a professional resume analysis assistant.

Analyze the resume below against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return the analysis as JSON with exactly these fields:

{{
    "summary": "short professional summary",
    "strengths": [
        "strength 1",
        "strength 2",
        "strength 3"
    ],
    "weaknesses": [
        "weakness 1",
        "weakness 2"
    ],
    "improvements": [
        "specific improvement 1",
        "specific improvement 2",
        "specific improvement 3"
    ],
    "rewritten_bullet": "rewrite one weak resume bullet into a stronger achievement-focused bullet",
    "interview_questions": [
        "question 1",
        "question 2",
        "question 3"
    ]
}}
"""

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are ResumeIQ. "
                        "Analyze resumes professionally. "
                        "Return only valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.3,

            response_format={
                "type": "json_object"
            }
        )

        content = response.choices[0].message.content

        analysis = json.loads(content)

        return {
            "available": True,
            "analysis": analysis
        }

    except Exception as error:

        return {
            "available": False,
            "message": f"AI analysis failed: {str(error)}"
        }