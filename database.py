import sqlite3


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

        str(data.get("skills", "")),

        str(data.get("education", "")),

        str(data.get("experience", "")),

        str(data.get("projects", "")),

        str(data.get("certifications", "")),

        str(data.get("achievements", "")),

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

    return data