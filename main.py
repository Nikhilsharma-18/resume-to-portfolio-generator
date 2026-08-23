import os
import json
from dotenv import load_dotenv
from google import genai


# Load .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY is missing.")
    exit()


# Gemini client
client = genai.Client(api_key=api_key)


def read_resume():

    try:
        with open("resume.txt", "r", encoding="utf-8") as file:
            resume = file.read()

    except FileNotFoundError:
        print("Error: resume.txt not found.")
        exit()

    lines = []

    for line in resume.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    resume = "\n".join(lines)

    if len(resume) < 50:
        print("Error: Resume is empty or too short.")
        exit()

    return resume


def create_prompt(resume):

    return f"""
Convert the following resume into portfolio data.

IMPORTANT:
- Use ONLY information present in the resume.
- Do not invent anything.
- Do not create fake skills.
- Do not create fake experience.
- Do not create fake projects.
- Do not create fake achievements.
- Do not create fake dates.
- Do not create fake links.
- If information is missing, use empty string or empty list.
- Return JSON only.
- Do not use markdown.

Use exactly this JSON structure:

{{
    "name": "",
    "headline": "",
    "summary": "",
    "skills": [],
    "education": [],
    "experience": [],
    "projects": [],
    "achievements": [],
    "contact": {{
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": ""
    }}
}}

Resume:

{resume}
"""


def get_gemini_data(prompt):

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        text = response.text.strip()

        # Remove markdown if Gemini adds it
        if text.startswith("```json"):
            text = text[7:]

        if text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        data = json.loads(text)

        return data

    except json.JSONDecodeError:

        print("Error: Gemini returned invalid JSON.")
        exit()

    except Exception as e:

        print("Gemini API error:", e)
        exit()


def make_list(items):

    if not items:
        return ""

    html = ""

    for item in items:
        html += f"<li>{item}</li>\n"

    return html


def make_sections(items):

    if not items:
        return ""

    html = ""

    for item in items:

        html += f"<p>{item}</p>\n"

    return html


def generate_portfolio(data):

    try:

        with open("template.html", "r", encoding="utf-8") as file:
            template = file.read()

    except FileNotFoundError:

        print("Error: template.html not found.")
        exit()


    contact = data.get("contact", {})

    html = template

    html = html.replace("{{ name }}", data.get("name", ""))
    html = html.replace("{{ headline }}", data.get("headline", ""))
    html = html.replace("{{ summary }}", data.get("summary", ""))

    html = html.replace(
        "{{ skills }}",
        make_list(data.get("skills", []))
    )

    html = html.replace(
        "{{ education }}",
        make_sections(data.get("education", []))
    )

    html = html.replace(
        "{{ experience }}",
        make_sections(data.get("experience", []))
    )

    html = html.replace(
        "{{ projects }}",
        make_sections(data.get("projects", []))
    )

    html = html.replace(
        "{{ achievements }}",
        make_sections(data.get("achievements", []))
    )

    html = html.replace(
        "{{ email }}",
        contact.get("email", "")
    )

    html = html.replace(
        "{{ phone }}",
        contact.get("phone", "")
    )

    html = html.replace(
        "{{ linkedin }}",
        contact.get("linkedin", "")
    )

    html = html.replace(
        "{{ github }}",
        contact.get("github", "")
    )


    with open("portfolio.html", "w", encoding="utf-8") as file:
        file.write(html)

    print("portfolio.html generated successfully!")


def main():

    print("Reading resume...")

    resume = read_resume()

    print("Resume loaded successfully.")

    print("Sending resume to Gemini...")

    prompt = create_prompt(resume)

    data = get_gemini_data(prompt)

    print("Gemini JSON received successfully.")

    generate_portfolio(data)


if __name__ == "__main__":
    main()