import sqlite3
import json
import ast


DATABASE = "portfolio.db"


# =========================
# Database Connection
# =========================

def get_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# =========================
# Create Database
# =========================

def init_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolios (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            portfolio_id TEXT UNIQUE NOT NULL,

            name TEXT,

            email TEXT,

            phone TEXT,

            linkedin TEXT,

            github TEXT,

            summary TEXT,

            skills TEXT,

            education TEXT,

            experience TEXT,

            projects TEXT,

            certifications TEXT,

            achievements TEXT,

            dob TEXT,

            languages TEXT,

            interests TEXT

        )
    """)

    connection.commit()

    connection.close()


# =========================
# Helper for serialization
# =========================

def _serialize_field(val):
    if val is None:
        return json.dumps([])
    if isinstance(val, (list, dict)):
        return json.dumps(val)
    return str(val)


# =========================
# Save Portfolio
# =========================

def save_portfolio(portfolio_id, data):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO portfolios (

            portfolio_id,
            name,
            email,
            phone,
            linkedin,
            github,
            summary,
            skills,
            education,
            experience,
            projects,
            certifications,
            achievements,
            dob,
            languages,
            interests

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        portfolio_id,

        data.get("name", ""),

        data.get("email", ""),

        data.get("phone", ""),

        data.get("linkedin", ""),

        data.get("github", ""),

        data.get("summary", ""),

        _serialize_field(data.get("skills", [])),

        _serialize_field(data.get("education", [])),

        _serialize_field(data.get("experience", [])),

        _serialize_field(data.get("projects", [])),

        _serialize_field(data.get("certifications", [])),

        _serialize_field(data.get("achievements", [])),

        data.get("dob", ""),

        data.get("languages", ""),

        data.get("interests", "")

    ))

    connection.commit()

    connection.close()


# =========================
# Get Portfolio
# =========================

def get_portfolio(portfolio_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM portfolios
        WHERE portfolio_id = ?
    """, (portfolio_id,))

    row = cursor.fetchone()

    connection.close()


    if not row:

        return None


    data = dict(row)

    data.pop("id", None)

    data.pop("portfolio_id", None)

    # Deserialize JSON fields
    json_fields = ["skills", "education", "experience", "projects", "certifications", "achievements"]
    for field in json_fields:
        raw_val = data.get(field)
        if raw_val:
            try:
                data[field] = json.loads(raw_val)
            except Exception:
                try:
                    data[field] = ast.literal_eval(raw_val)
                except Exception:
                    data[field] = raw_val
        else:
            data[field] = []

    return data