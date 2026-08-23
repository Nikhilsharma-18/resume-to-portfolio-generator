import re


# =========================================================
# CLEAN TEXT
# =========================================================

def clean_resume_text(text):
    """Clean Markdown, HTML and unnecessary formatting."""

    if not text:
        return ""

    # Normalize line breaks
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove markdown headings
    text = re.sub(
        r"^#{1,6}\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    # Remove markdown bold / italic
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("*", "")

    # HTML line breaks
    text = re.sub(
        r"<br\s*/?>",
        "\n",
        text,
        flags=re.IGNORECASE
    )

    # HTML formatting tags
    text = re.sub(
        r"</?(b|strong|i|em)>",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove remaining HTML tags
    text = re.sub(
        r"<[^>]+>",
        "",
        text
    )

    # Normalize dashes
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Remove unnecessary spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# BASIC INFORMATION
# =========================================================

def extract_email(text):

    match = re.search(
        r"[\w.-]+@[\w.-]+\.\w+",
        text
    )

    return match.group(0) if match else ""


def extract_phone(text):

    match = re.search(
        r"(\+91[\s-]?)?[6-9]\d{9}",
        text
    )

    return match.group(0) if match else ""


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


# =========================================================
# NAME
# =========================================================

def extract_name(text):

    text = clean_resume_text(text)

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return "Your Name"

    for line in lines[:10]:

        if (
            "@" not in line
            and not re.search(r"\d", line)
            and len(line.split()) <= 5
            and len(line) > 2
        ):
            return line

    return "Your Name"


# =========================================================
# SECTION DEFINITIONS
# =========================================================

COMMON_SECTIONS = {
    "skills",
    "technical skills",
    "key skills",

    "education",
    "academic background",

    "experience",
    "work experience",
    "professional experience",
    "internship",
    "internship / experience",

    "projects",
    "personal projects",
    "academic projects",

    "achievements",
    "achievements & activities",
    "accomplishments",
    "awards",

    "certifications",
    "certificates",

    "contact",
    "summary",
    "profile",
    "professional summary",
    "career objective",
    "objective",

    "personal details"
}


# =========================================================
# SECTION EXTRACTION
# =========================================================

def extract_section(text, section_names):

    text = clean_resume_text(text)

    lines = text.splitlines()

    start = None

    for i, line in enumerate(lines):

        cleaned = line.strip().lower()

        if cleaned in section_names:

            start = i + 1
            break

    if start is None:
        return ""

    section = []

    for line in lines[start:]:

        cleaned = line.strip().lower()

        if cleaned in COMMON_SECTIONS:
            break

        if line.strip():
            section.append(line.strip())

    return "\n".join(section)


# =========================================================
# SKILLS
# =========================================================

KNOWN_SKILLS = [
    "C++",
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "HTML",
    "CSS",
    "React.js",
    "React",
    "Node.js",
    "Node",
    "Flask",
    "Django",
    "Bootstrap",
    "Tailwind CSS",
    "MySQL",
    "MongoDB",
    "PostgreSQL",
    "SQLite",
    "Git",
    "GitHub",
    "VS Code",
    "Visual Studio Code",
    "Docker",
    "Data Structures & Algorithms",
    "Data Structures",
    "Algorithms",
    "OOP",
    "Object Oriented Programming",
    "DBMS",
    "Computer Networks",
    "Operating Systems",
    "REST API",
    "REST APIs",
    "Machine Learning",
    "Artificial Intelligence"
]


def extract_skills(text):

    skills_section = extract_section(
        text,
        {
            "skills",
            "technical skills",
            "key skills"
        }
    )

    if not skills_section:
        return []

    searchable_text = clean_resume_text(
        skills_section
    )

    searchable_text = searchable_text.replace(
        "\n",
        " "
    )

    searchable_text = searchable_text.replace(
        "•",
        " "
    )

    searchable_text = searchable_text.replace(
        "|",
        " "
    )

    found = []

    for skill in sorted(
        KNOWN_SKILLS,
        key=len,
        reverse=True
    ):

        if re.search(
            rf"(?<!\w){re.escape(skill)}(?!\w)",
            searchable_text,
            re.IGNORECASE
        ):

            # Avoid duplicate React
            if (
                skill.lower() == "react"
                and any(
                    x.lower() == "react.js"
                    for x in found
                )
            ):
                continue

            # Avoid duplicate Node
            if (
                skill.lower() == "node"
                and any(
                    x.lower() == "node.js"
                    for x in found
                )
            ):
                continue

            # Avoid duplicate Data Structures
            if (
                skill.lower() == "data structures"
                and any(
                    x.lower()
                    == "data structures & algorithms"
                    for x in found
                )
            ):
                continue

            # Avoid duplicate Algorithms
            if (
                skill.lower() == "algorithms"
                and any(
                    x.lower()
                    == "data structures & algorithms"
                    for x in found
                )
            ):
                continue

            found.append(skill)

    return [
        skill
        for skill in KNOWN_SKILLS
        if skill in found
    ]


# =========================================================
# EDUCATION
# =========================================================

def extract_education(text):

    education_text = extract_section(
        text,
        {
            "education",
            "academic background"
        }
    )

    if not education_text:
        return []

    education_text = clean_resume_text(
        education_text
    )

    education_text = (
        education_text
        .replace("–", "-")
        .replace("—", "-")
    )

    lines = [
        line.strip()
        for line in education_text.splitlines()
        if line.strip()
    ]

    education = []

    current = None

    for line in lines:

        year_match = re.search(
            r"\b(19|20)\d{2}\s*-\s*(19|20)\d{2}\b",
            line
        )

        if year_match:

            if current:
                education.append(current)

            current = {
                "duration": year_match.group(0),
                "degree": "",
                "institution": "",
                "details": "",
                "cgpa": "",
                "percentage": ""
            }

            remaining = (
                line[:year_match.start()]
                +
                line[year_match.end():]
            ).strip()

            if remaining:
                current["degree"] = remaining

            continue

        if current is None:
            continue

        if not current["degree"]:

            current["degree"] = line

        elif not current["institution"]:

            current["institution"] = line

        else:

            if current["details"]:

                current["details"] += " " + line

            else:

                current["details"] = line

    if current:
        education.append(current)

    # Extract CGPA / Percentage

    for item in education:

        details = item["details"]

        cgpa_match = re.search(
            r"CGPA\s*[:\-]?\s*([\d.]+)",
            details,
            re.IGNORECASE
        )

        percentage_match = re.search(
            r"Percentage\s*[:\-]?\s*([\d.]+)\s*%?",
            details,
            re.IGNORECASE
        )

        if cgpa_match:

            item["cgpa"] = cgpa_match.group(1)

            details = re.sub(
                r"CGPA\s*[:\-]?\s*[\d.]+(?:\s*/\s*10)?",
                "",
                details,
                flags=re.IGNORECASE
            )

        if percentage_match:

            item["percentage"] = (
                percentage_match.group(1)
            )

            details = re.sub(
                r"Percentage\s*[:\-]?\s*[\d.]+\s*%?",
                "",
                details,
                flags=re.IGNORECASE
            )

        item["details"] = details.strip()

    return education


# =========================================================
# PROJECTS
# =========================================================

def extract_projects(text):

    projects_text = extract_section(
        text,
        {
            "projects",
            "personal projects",
            "academic projects"
        }
    )

    if not projects_text:
        return []

    projects_text = clean_resume_text(
        projects_text
    )

    lines = [
        line.strip()
        for line in projects_text.splitlines()
        if line.strip()
    ]

    projects = []

    current_title = None
    current_description = []

    for line in lines:

        if "—" in line or " - " in line:

            if current_title:

                projects.append({
                    "title": current_title,
                    "description":
                        " ".join(current_description)
                })

            if "—" in line:

                parts = line.split(
                    "—",
                    1
                )

            else:

                parts = line.split(
                    " - ",
                    1
                )

            current_title = parts[0].strip()

            current_description = []

            if len(parts) > 1:

                current_description.append(
                    parts[1].strip()
                )

        else:

            if current_title:

                current_description.append(
                    line
                )

            else:

                current_title = line

    if current_title:

        projects.append({
            "title": current_title,
            "description":
                " ".join(current_description)
        })

    return projects


# =========================================================
# EXPERIENCE
# =========================================================

def extract_experience(text):

    if not text:
        return []

    text = clean_resume_text(text)

    # -----------------------------------------------------
    # Get Experience section
    # -----------------------------------------------------

    experience_text = extract_section(
        text,
        {
            "experience",
            "work experience",
            "professional experience",
            "internship",
            "internship / experience"
        }
    )

    if not experience_text:

        return []

    # -----------------------------------------------------
    # Clean formatting
    # -----------------------------------------------------

    experience_text = clean_resume_text(
        experience_text
    )

    # Convert bullets to spaces
    experience_text = experience_text.replace(
        "•",
        " "
    )

    # Normalize whitespace
    experience_text = re.sub(
        r"\s+",
        " ",
        experience_text
    ).strip()

    # -----------------------------------------------------
    # Find date
    #
    # May 2026 - July 2026
    # -----------------------------------------------------

    date_pattern = re.compile(
        r"([A-Za-z]{3,9}\s+\d{4})"
        r"\s*-\s*"
        r"([A-Za-z]{3,9}\s+\d{4})",
        re.IGNORECASE
    )

    date_match = date_pattern.search(
        experience_text
    )

    if not date_match:

        return []

    date = (
        date_match.group(1)
        + " - "
        + date_match.group(2)
    )

    # -----------------------------------------------------
    # Header before date
    # -----------------------------------------------------

    header = experience_text[
        :date_match.start()
    ].strip()

    header = re.sub(
        r"[|,:;\-]+\s*$",
        "",
        header
    ).strip()

    # -----------------------------------------------------
    # Description after date
    # -----------------------------------------------------

    description = experience_text[
        date_match.end():
    ].strip()

    description = re.sub(
        r"^[|,:;\-]+\s*",
        "",
        description
    )

    description = re.sub(
        r"\s+",
        " ",
        description
    ).strip()

    # -----------------------------------------------------
    # Separate Title and Company
    # -----------------------------------------------------

    title = ""
    company = ""

    # Format:
    #
    # Web Development Intern - TechNova Solutions
    #

    if " - " in header:

        parts = header.split(
            " - ",
            1
        )

        title = parts[0].strip()
        company = parts[1].strip()

    # Format:
    #
    # Web Development Intern | TechNova Solutions
    #

    elif "|" in header:

        parts = header.split(
            "|",
            1
        )

        title = parts[0].strip()
        company = parts[1].strip()

    # Format:
    #
    # Web Development Intern
    # TechNova Solutions
    #

    else:

        header_lines = [
            x.strip()
            for x in header.splitlines()
            if x.strip()
        ]

        if len(header_lines) >= 2:

            title = header_lines[0]
            company = header_lines[1]

        elif len(header_lines) == 1:

            title = header_lines[0]

    # -----------------------------------------------------
    # Final cleaning
    # -----------------------------------------------------

    title = clean_resume_text(title)
    company = clean_resume_text(company)
    date = clean_resume_text(date)
    description = clean_resume_text(description)

    return [
        {
            "title": title,
            "company": company,
            "date": date,
            "description": description
        }
    ]


# =========================================================
# LIST SECTIONS
# =========================================================

def extract_list_section(
    text,
    section_names
):

    section = extract_section(
        text,
        section_names
    )

    if not section:
        return []

    section = clean_resume_text(
        section
    )

    result = []

    for line in section.splitlines():

        line = line.strip()

        if not line:
            continue

        line = re.sub(
            r"^[•\-\*]\s*",
            "",
            line
        )

        result.append(line)

    return result


# =========================================================
# CERTIFICATIONS
# =========================================================

def extract_certifications(text):

    return extract_list_section(
        text,
        {
            "certifications",
            "certificates"
        }
    )


# =========================================================
# FINAL DATA
# =========================================================

def extract_resume_data(text):

    text = clean_resume_text(text)

    return {

        "name":
            extract_name(text),

        "email":
            extract_email(text),

        "phone":
            extract_phone(text),

        "linkedin":
            extract_linkedin(text),

        "github":
            extract_github(text),

        "summary":
            extract_section(
                text,
                {
                    "summary",
                    "profile",
                    "professional summary",
                    "career objective",
                    "objective"
                }
            ),

        "skills":
            extract_skills(text),

        "education":
            extract_education(text),

        "experience":
            extract_experience(text),

        "projects":
            extract_projects(text),

        "achievements":
            extract_list_section(
                text,
                {
                    "achievements",
                    "achievements & activities",
                    "accomplishments",
                    "awards"
                }
            ),

        "certifications":
            extract_certifications(text)
    }