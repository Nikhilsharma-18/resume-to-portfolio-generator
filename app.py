from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from parser import extract_resume_data

from database import (
    init_database,
    save_portfolio,
    get_portfolio
)

import os
import uuid

from pypdf import PdfReader
from docx import Document


app = Flask(__name__)


# =========================
# Configuration
# =========================

UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx"
}

MAX_FILE_SIZE = 10 * 1024 * 1024

app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================
# Initialize Database
# =========================

init_database()


# =========================
# File Validation
# =========================

def allowed_file(filename):

    if not filename:
        return False

    extension = os.path.splitext(
        filename
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


# =========================
# PDF Text Extraction
# =========================

def extract_pdf_text(filepath):

    text = ""

    reader = PdfReader(filepath)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            text += page_text + "\n"

    return text.strip()


# =========================
# DOCX Text Extraction
# =========================

def extract_docx_text(filepath):

    text = ""

    document = Document(filepath)

    for paragraph in document.paragraphs:

        if paragraph.text.strip():

            text += paragraph.text + "\n"

    return text.strip()


# =========================
# Home
# =========================

@app.route("/")
def home():

    return render_template(
        "upload.html"
    )


# =========================
# Upload Resume
# =========================

@app.route(
    "/upload",
    methods=["POST"]
)
def upload_resume():

    # Check file
    if "resume" not in request.files:

        return render_template(
            "upload.html",
            error="Please select a resume file."
        )


    file = request.files["resume"]


    # Empty filename
    if file.filename == "":

        return render_template(
            "upload.html",
            error="Please select a resume."
        )


    # Validate extension
    if not allowed_file(
        file.filename
    ):

        return render_template(
            "upload.html",
            error=(
                "Only PDF and DOCX "
                "files are supported."
            )
        )


    # Secure filename
    original_filename = secure_filename(
        file.filename
    )


    # Unique filename
    unique_filename = (
        uuid.uuid4().hex
        + "_"
        + original_filename
    )


    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        unique_filename
    )


    try:

        # Save file
        file.save(filepath)


        # Determine file type
        extension = os.path.splitext(
            original_filename
        )[1].lower()


        # Extract text
        if extension == ".pdf":

            resume_text = extract_pdf_text(
                filepath
            )

        elif extension == ".docx":

            resume_text = extract_docx_text(
                filepath
            )

        else:

            resume_text = ""


        # Empty text
        if not resume_text.strip():

            return render_template(
                "upload.html",
                error=(
                    "We couldn't extract text "
                    "from this file. Please upload "
                    "a text-based PDF or DOCX."
                )
            )


        # =========================
        # Parse Resume
        # =========================

        resume_data = extract_resume_data(
            resume_text
        )


        # =========================
        # Create Portfolio ID
        # =========================

        portfolio_id = uuid.uuid4().hex[:8]


        # =========================
        # Save to Database
        # =========================

        save_portfolio(
            portfolio_id,
            resume_data
        )


        # =========================
        # Render Portfolio
        # =========================

        return render_template(
            "template.html",
            **resume_data,
            portfolio_id=portfolio_id
        )


    except Exception as error:

        print(
            "Resume processing error:",
            error
        )


        return render_template(
            "upload.html",
            error=(
                "Something went wrong while "
                "processing your resume."
            )
        )


    finally:

        # Delete uploaded file
        if os.path.exists(filepath):

            try:

                os.remove(filepath)

            except Exception:

                pass


# =========================
# Shareable Portfolio
# =========================

@app.route(
    "/portfolio/<portfolio_id>"
)
def view_portfolio(portfolio_id):

    data = get_portfolio(
        portfolio_id
    )


    if not data:

        return (
            "Portfolio not found.",
            404
        )


    return render_template(
        "template.html",
        **data,
        portfolio_id=portfolio_id
    )


# =========================
# File Too Large
# =========================

@app.errorhandler(413)
def file_too_large(error):

    return render_template(
        "upload.html",
        error=(
            "File is too large. "
            "Maximum allowed size is 10 MB."
        )
    ), 413


# =========================
# Run
# =========================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )