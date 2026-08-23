import os


def read_resume(file_path="resume.txt"):
    if not os.path.exists(file_path):
        print("Error: resume.txt file not found.")
        return None

    with open(file_path, "r", encoding="utf-8") as file:
        resume_text = file.read()

    if not resume_text.strip():
        print("Error: Resume file is empty.")
        return None

    return resume_text

def clean_resume(resume_text):
    lines = resume_text.splitlines()

    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

def validate_resume(resume_text, minimum_length=50):
    if len(resume_text) < minimum_length:
        print("Error: Resume is too short.")
        return False

    return True

def get_processed_resume(file_path="resume.txt"):
    resume = read_resume(file_path)

    if resume is None:
        return None

    cleaned_resume = clean_resume(resume)

    if not validate_resume(cleaned_resume):
        return None

    return cleaned_resume