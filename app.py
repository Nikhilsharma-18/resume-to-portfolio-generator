from flask import Flask, render_template, request, redirect, url_for, make_response
from werkzeug.utils import secure_filename

from parser import extract_resume_data

from database import (
    init_database,
    save_portfolio,
    get_portfolio
)

import os
import uuid
import io
import zipfile

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


        # Redirect to persistent shareable portfolio URL
        return redirect(
            url_for(
                "view_portfolio",
                portfolio_id=portfolio_id
            )
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
# Standalone HTML Download
# =========================

@app.route(
    "/portfolio/<portfolio_id>/export/html"
)
def export_portfolio_html(portfolio_id):

    data = get_portfolio(portfolio_id)

    if not data:
        return ("Portfolio not found.", 404)

    css_path = os.path.join(app.static_folder, "style.css")
    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

    js_path = os.path.join(app.static_folder, "script.js")
    js_content = ""
    if os.path.exists(js_path):
        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()

    rendered_html = render_template(
        "template.html",
        **data,
        portfolio_id=portfolio_id,
        standalone_download=True,
        inline_css=css_content,
        inline_js=js_content
    )

    name = (data.get("name") or "my").strip()
    safe_name = "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-") or "my"
    filename = f"{safe_name}-portfolio.html"

    response = make_response(rendered_html)
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


# =========================
# Full ZIP Package Export (HTML, CSS, JS)
# =========================

@app.route(
    "/portfolio/<portfolio_id>/export/zip"
)
def export_portfolio_zip(portfolio_id):

    data = get_portfolio(portfolio_id)

    if not data:
        return ("Portfolio not found.", 404)

    css_path = os.path.join(app.static_folder, "style.css")
    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

    js_path = os.path.join(app.static_folder, "script.js")
    js_content = ""
    if os.path.exists(js_path):
        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()

    # Render index.html pointing to local relative style.css and script.js
    rendered_html = render_template(
        "template.html",
        **data,
        portfolio_id=portfolio_id,
        zip_download=True
    )

    name = (data.get("name") or "my").strip()
    safe_name = "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-") or "my"
    
    readme_content = f"""# {data.get("name", "User")}'s Portfolio

This portfolio bundle contains:
- `index.html`: The main portfolio HTML structure
- `style.css`: All portfolio styles, themes, and layout rules
- `script.js`: Interactive elements, share options, and print handlers

## How to View Locally
Simply double click `index.html` to open your portfolio in any browser.

## How to Deploy
You can upload these files (`index.html`, `style.css`, `script.js`) to GitHub Pages, Netlify, or Vercel for free web hosting!
"""

    # Create ZIP archive in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("index.html", rendered_html)
        zip_file.writestr("style.css", css_content)
        zip_file.writestr("script.js", js_content)
        zip_file.writestr("README.md", readme_content)

    zip_buffer.seek(0)
    filename = f"{safe_name}-portfolio.zip"

    response = make_response(zip_buffer.getvalue())
    response.headers["Content-Type"] = "application/zip"
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response




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