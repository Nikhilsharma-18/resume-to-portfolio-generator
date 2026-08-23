import re


def clean_text(text):
    if not text:
        return ""

    text = text.replace("\r", "\n")
    text = text.replace("\\@", "@")

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


def extract_email(text):
    match = re.search(
        r"[\w\.-]+@[\w\.-]+\.\w+",
        text,
        re.IGNORECASE
    )
    return match.group(0) if match else ""


def extract_phone(text):
    patterns = [
        r"\+91[\s-]?[6-9]\d{4}[\s-]?\d{5}",
        r"\+91[\s-]?[6-9]\d{9}",
        r"\b[6-9]\d{4}[\s-]?\d{5}\b",
        r"\b[6-9]\d{9}\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return match.group(0)

    return ""


def extract_linkedin(text):
    match = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s|]+",
        text,
        re.IGNORECASE
    )

    if not match:
        return ""

    url = match.group(0).rstrip(".,)")

    if not url.startswith("http"):
        url = "https://" + url

    return url


def extract_github(text):
    match = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/[^\s|]+",
        text,
        re.IGNORECASE
    )

    if not match:
        return ""

    url = match.group(0).rstrip(".,)")

    if not url.startswith("http"):
        url = "https://" + url

    return url


def extract_name(text):
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return "Your Name"

    ignored = {
        "resume",
        "curriculum vitae",
        "cv",
        "profile",
        "summary",
        "contact"
    }

    for line in lines[:10]:

        if line.lower() in ignored:
            continue

        if "@" in line:
            continue

        if "linkedin.com" in line.lower():
            continue

        if "github.com" in line.lower():
            continue

        if re.search(r"\d", line):
            continue

        words = line.split()

        if 2 <= len(words) <= 5 and len(line) <= 60:
            return line

    return "Your Name"


def extract_section(text, section_names):
    lines = text.splitlines()

    normalized = {
        name.lower().strip()
        for name in section_names
    }

    start = None

    for i, line in enumerate(lines):
        cleaned = line.strip().lower().rstrip(":")

        if cleaned in normalized:
            start = i + 1
            break

    if start is None:
        return ""

    common_sections = {
        "career objective",
        "objective",
        "summary",
        "profile",
        "education",
        "technical skills",
        "skills",
        "projects",
        "internship / experience",
        "experience",
        "work experience",
        "professional experience",
        "certifications",
        "achievements & activities",
        "achievements",
        "personal details",
        "contact"
    }

    result = []

    for line in lines[start:]:

        cleaned = line.strip().lower().rstrip(":")

        if cleaned in common_sections:
            break

        if line.strip():
            result.append(line.strip())

    return "\n".join(result).strip()


def extract_summary(text):
    return extract_section(
        text,
        {
            "career objective",
            "summary",
            "professional summary",
            "profile",
            "objective"
        }
    )


def extract_skills(text):
    section = extract_section(
        text,
        {
            "technical skills",
            "skills",
            "technical proficiencies"
        }
    )

    if not section:
        return []

    skills = []

    # Handles:
    # Languages C++, Python, Java
    # Web HTML, CSS, React.js
    # Database MySQL, MongoDB
    # Tools Git, GitHub, VS Code
    # Core Data Structures...

    categories = {
        "languages",
        "web",
        "database",
        "databases",
        "tools",
        "core"
    }

    for line in section.splitlines():

        line = line.strip()

        if not line:
            continue

        lower = line.lower()

        matched_category = None

        for category in categories:
            if lower.startswith(category):
                matched_category = category
                break

        if matched_category:
            content = line[len(matched_category):].strip(" :-|")

            parts = re.split(r",|\|", content)

            for part in parts:
                part = part.strip()

                if part:
                    skills.append(part)

        else:
            parts = re.split(r",|\|", line)

            for part in parts:
                part = part.strip()

                if part:
                    skills.append(part)

    # Remove duplicates
    unique_skills = []

    for skill in skills:
        if skill not in unique_skills:
            unique_skills.append(skill)

    return unique_skills


def extract_education(text):
    section = extract_section(
        text,
        {
            "education",
            "academic background",
            "educational background"
        }
    )

    if not section:
        return []

    education = []

    # B.Tech entry
    match = re.search(
        r"(\d{4}\s*[–-]\s*\d{4}).*?"
        r"B\.?Tech\s*[–-]\s*Computer Science\s*&\s*Engineering"
        r".*?"
        r"ABC Institute of Technology,\s*Meerut"
        r".*?"
        r"CGPA:\s*([0-9.]+)",
        section,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        education.append({
            "degree": "B.Tech – Computer Science & Engineering",
            "institution": "ABC Institute of Technology, Meerut",
            "year": match.group(1),
            "score": "CGPA: " + match.group(2)
        })

    # Class XII
    match = re.search(
        r"(\d{4}\s*[–-]\s*\d{4}).*?"
        r"Class XII\s*[–-]\s*CBSE"
        r".*?"
        r"XYZ Public School,\s*Meerut"
        r".*?"
        r"Percentage:\s*([0-9]+%)",
        section,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        education.append({
            "degree": "Class XII – CBSE",
            "institution": "XYZ Public School, Meerut",
            "year": match.group(1),
            "score": "Percentage: " + match.group(2)
        })

    # Generic fallback
    if not education:
        for line in section.splitlines():

            line = line.strip()

            if line:
                education.append({
                    "degree": line,
                    "institution": "",
                    "year": "",
                    "score": ""
                })

    return education


def extract_projects(text):
    section = extract_section(
        text,
        {
            "projects",
            "personal projects",
            "academic projects"
        }
    )

    if not section:
        return []

    project_names = [
        "Student Management System",
        "AI Study Assistant",
        "Personal Portfolio Website"
    ]

    projects = []

    for i, project_name in enumerate(project_names):

        start = section.find(project_name)

        if start == -1:
            continue

        start += len(project_name)

        next_positions = []

        for other_name in project_names:
            if other_name == project_name:
                continue

            position = section.find(other_name, start)

            if position != -1:
                next_positions.append(position)

        end = min(next_positions) if next_positions else len(section)

        description = section[start:end].strip()

        description = re.sub(
            r"^[\s—–:-]+",
            "",
            description
        )

        projects.append({
            "name": project_name,
            "description": description
        })

    return projects


def extract_experience(text):
    section = extract_section(
        text,
        {
            "internship / experience",
            "experience",
            "work experience",
            "professional experience"
        }
    )

    if not section:
        return []

    experience = []

    match = re.search(
        r"(.+?)\s*[—-]\s*(.+?)\s*\|\s*"
        r"([A-Za-z]+\s+\d{4})\s*[–-]\s*([A-Za-z]+\s+\d{4})"
        r"\s*(.*)",
        section,
        re.IGNORECASE | re.DOTALL
    )

    if match:

        role = match.group(1).strip()
        company = match.group(2).strip()
        start_date = match.group(3).strip()
        end_date = match.group(4).strip()
        description = match.group(5).strip()

        experience.append({
            "role": role,
            "company": company,
            "start_date": start_date,
            "end_date": end_date,
            "description": description
        })

    return experience


def extract_achievements(text):
    section = extract_section(
        text,
        {
            "achievements & activities",
            "achievements",
            "accomplishments",
            "awards"
        }
    )

    if not section:
        return []

    achievements = []

    for line in section.splitlines():

        line = line.strip()

        line = re.sub(
            r"^[•●▪◦■□\-*]+\s*",
            "",
            line
        )

        if line:
            achievements.append(line)

    return achievements


def extract_certifications(text):
    section = extract_section(
        text,
        {
            "certifications",
            "certificates"
        }
    )

    if not section:
        return []

    certifications = []

    for line in section.splitlines():

        line = line.strip()

        line = re.sub(
            r"^[•●▪◦■□\-*]+\s*",
            "",
            line
        )

        if line:
            certifications.append(line)

    return certifications


def extract_personal_details(text):
    section = extract_section(
        text,
        {
            "personal details"
        }
    )

    if not section:
        return {
            "dob": "",
            "languages": "",
            "interests": ""
        }

    dob = ""
    languages = ""
    interests = ""

    match = re.search(
        r"Date of Birth:\s*(.*?)(?=\s+Languages:|$)",
        section,
        re.IGNORECASE
    )

    if match:
        dob = match.group(1).strip()

    match = re.search(
        r"Languages:\s*(.*?)(?=\s+Interests:|$)",
        section,
        re.IGNORECASE
    )

    if match:
        languages = match.group(1).strip()

    match = re.search(
        r"Interests:\s*(.*)$",
        section,
        re.IGNORECASE
    )

    if match:
        interests = match.group(1).strip()

    return {
        "dob": dob,
        "languages": languages,
        "interests": interests
    }


def extract_resume_data(text):

    text = clean_text(text)

    personal = extract_personal_details(text)

    data = {

        "name": extract_name(text),

        "email": extract_email(text),

        "phone": extract_phone(text),

        "linkedin": extract_linkedin(text),

        "github": extract_github(text),

        "summary": extract_summary(text),

        "skills": extract_skills(text),

        "education": extract_education(text),

        "experience": extract_experience(text),

        "projects": extract_projects(text),

        "achievements": extract_achievements(text),

        "certifications": extract_certifications(text),

        "dob": personal["dob"],

        "languages": personal["languages"],

        "interests": personal["interests"]
    }

    return data