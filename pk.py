import os
import sqlite3
import hashlib
import json
import secrets
import string
from datetime import datetime, date
from pathlib import Path

import streamlit as st


# ============================================================
# OPTIONAL PACKAGES
# ============================================================

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
except ImportError:
    canvas = None

try:
    from docx import Document
except ImportError:
    Document = None


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PADHO PAKISTAN",
    page_icon="🇵🇰",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"

DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "padho_pakistan.db"


# ============================================================
# 50 AGENTS
# ============================================================

AGENTS = [
    ("01", "Student Management Agent", "Academic"),
    ("02", "Teacher Management Agent", "Academic"),
    ("03", "Course Management Agent", "Academic"),
    ("04", "Subject Management Agent", "Academic"),
    ("05", "Class Management Agent", "Academic"),
    ("06", "Enrollment Agent", "Academic"),
    ("07", "Assignment Agent", "Academic"),
    ("08", "Assignment Submission Agent", "Academic"),
    ("09", "Assignment Grading Agent", "Academic"),
    ("10", "Quiz Agent", "Academic"),
    ("11", "Quiz Evaluation Agent", "Academic"),
    ("12", "Exam Management Agent", "Academic"),
    ("13", "Question Bank Agent", "Academic"),
    ("14", "AI Question Generator Agent", "AI"),
    ("15", "Attendance Agent", "Academic"),
    ("16", "Timetable Agent", "Academic"),
    ("17", "Study Material Agent", "Academic"),
    ("18", "AI Tutor Agent", "AI"),
    ("19", "AI Lesson Planner Agent", "AI"),
    ("20", "Curriculum Agent", "Academic"),
    ("21", "Student Performance Agent", "Student"),
    ("22", "Personalized Learning Agent", "Student"),
    ("23", "Study Planner Agent", "Student"),
    ("24", "Reminder Agent", "Student"),
    ("25", "Notification Agent", "Communication"),
    ("26", "Certificate Agent", "Student"),
    ("27", "Achievement Agent", "Student"),
    ("28", "Career Guidance Agent", "AI"),
    ("29", "Coding Practice Agent", "AI"),
    ("30", "Project/FYP Agent", "Academic"),
    ("31", "Teacher Assistant Agent", "Teacher"),
    ("32", "AI Content Generator Agent", "AI"),
    ("33", "Rubric Agent", "Teacher"),
    ("34", "Feedback Agent", "Teacher"),
    ("35", "Analytics Agent", "Analytics"),
    ("36", "Dashboard Agent", "System"),
    ("37", "Report Generator Agent", "Reports"),
    ("38", "PDF Generator Agent", "Documents"),
    ("39", "Word Document Agent", "Documents"),
    ("40", "Excel Agent", "Documents"),
    ("41", "Announcement Agent", "Communication"),
    ("42", "Email Agent", "Communication"),
    ("43", "Discussion Agent", "Communication"),
    ("44", "Chatbot Agent", "AI"),
    ("45", "Search Agent", "System"),
    ("46", "File Management Agent", "System"),
    ("47", "Authentication Agent", "Security"),
    ("48", "Security Agent", "Security"),
    ("49", "Database Agent", "System"),
    ("50", "System Administration Agent", "System"),
]

AGENT_DESCRIPTIONS = {
    name: f"{name} handles {category.lower()} related LMS activities."
    for _, name, category in AGENTS
}


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "logged_in": False,
    "username": "",
    "role": "",
    "user_id": None,
    "page": "Dashboard",
    "selected_agent": None,
    "chat_messages": [],
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def execute(query, params=(), fetch=False, many=False):
    conn = get_db()

    try:
        cur = conn.cursor()

        if many:
            cur.executemany(query, params)
        else:
            cur.execute(query, params)

        if fetch:
            result = cur.fetchall()
        else:
            result = cur.lastrowid

        conn.commit()
        return result

    finally:
        conn.close()


# ============================================================
# PASSWORD SECURITY
# ============================================================

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def generate_password(length=10):
    characters = string.ascii_letters + string.digits
    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db():

    conn = get_db()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT,
            department TEXT,
            semester TEXT,
            status TEXT DEFAULT 'Active',
            created_at TEXT,
            last_login TEXT
        );

        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            name TEXT NOT NULL,
            department TEXT,
            credit_hours INTEGER DEFAULT 3,
            teacher TEXT,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            title TEXT,
            description TEXT,
            due_date TEXT,
            total_marks REAL,
            teacher TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER,
            student TEXT,
            submission_text TEXT,
            file_name TEXT,
            submitted_at TEXT,
            marks REAL DEFAULT 0,
            feedback TEXT,
            status TEXT
        );

        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course TEXT,
            title TEXT,
            questions TEXT,
            duration INTEGER,
            total_marks REAL,
            teacher TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            student TEXT,
            score REAL,
            percentage REAL,
            submitted_at TEXT
        );

        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student TEXT,
            course TEXT,
            attendance_date TEXT,
            status TEXT
        );

        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student TEXT,
            course TEXT,
            marks REAL,
            grade TEXT,
            grade_point REAL,
            semester TEXT
        );

        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course TEXT,
            title TEXT,
            file_name TEXT,
            uploaded_by TEXT,
            uploaded_at TEXT
        );

        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT,
            created_at TEXT,
            is_read INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            message TEXT,
            posted_by TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS agent_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            request TEXT,
            selected_agent TEXT,
            status TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """
    )

    # Migration for older database versions
    try:
        cur.execute(
            "ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'Active'"
        )
    except sqlite3.OperationalError:
        pass

    try:
        cur.execute(
            "ALTER TABLE users ADD COLUMN last_login TEXT"
        )
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

    create_demo_users()
    create_demo_courses()
    create_demo_assignments()
    create_demo_quizzes()


# ============================================================
# DEMO USERS
# ============================================================

def create_demo_users():

    users = [
        (
            "admin",
            "admin123",
            "System Administrator",
            "Admin",
            "admin@padhopakistan.pk",
            "Administration",
            "",
        ),
        (
            "teacher",
            "teacher123",
            "Demo Teacher",
            "Teacher",
            "teacher@padhopakistan.pk",
            "Computer Science",
            "",
        ),
        (
            "student",
            "student123",
            "Demo Student",
            "Student",
            "student@padhopakistan.pk",
            "Computer Science",
            "5",
        ),
    ]

    for user in users:

        exists = execute(
            "SELECT id FROM users WHERE username=?",
            (user[0],),
            fetch=True,
        )

        if not exists:

            execute(
                """
                INSERT INTO users
                (
                    username,
                    password,
                    name,
                    role,
                    email,
                    department,
                    semester,
                    status,
                    created_at
                )
                VALUES (?,?,?,?,?,?,?,?,?)
                """,
                (
                    user[0],
                    hash_password(user[1]),
                    user[2],
                    user[3],
                    user[4],
                    user[5],
                    user[6],
                    "Active",
                    datetime.now().isoformat(),
                ),
            )


# ============================================================
# DEMO COURSES
# ============================================================

def create_demo_courses():

    count = execute(
        "SELECT COUNT(*) AS c FROM courses",
        fetch=True,
    )[0]["c"]

    if count > 0:
        return

    courses = [
        (
            "AI101",
            "Artificial Intelligence",
            "Computer Science",
            3,
        ),
        (
            "PY101",
            "Python Programming",
            "Computer Science",
            3,
        ),
        (
            "DS101",
            "Data Science",
            "Computer Science",
            3,
        ),
        (
            "ML101",
            "Machine Learning",
            "Computer Science",
            3,
        ),
        (
            "WEB101",
            "Web Development",
            "Computer Science",
            3,
        ),
    ]

    for code, name, dept, credit in courses:

        execute(
            """
            INSERT INTO courses
            (
                code,
                name,
                department,
                credit_hours,
                teacher,
                description
            )
            VALUES (?,?,?,?,?,?)
            """,
            (
                code,
                name,
                dept,
                credit,
                "Demo Teacher",
                f"Complete course on {name}.",
            ),
        )


# ============================================================
# DEMO ASSIGNMENTS
# ============================================================

def create_demo_assignments():

    count = execute(
        "SELECT COUNT(*) AS c FROM assignments",
        fetch=True,
    )[0]["c"]

    if count > 0:
        return

    courses = execute(
        "SELECT id,name FROM courses",
        fetch=True,
    )

    for i, course in enumerate(courses[:5], start=1):

        execute(
            """
            INSERT INTO assignments
            (
                course_id,
                title,
                description,
                due_date,
                total_marks,
                teacher,
                created_at
            )
            VALUES (?,?,?,?,?,?,?)
            """,
            (
                course["id"],
                f"{course['name']} Assignment {i}",
                f"Complete the practical assignment for {course['name']}.",
                "2026-10-20",
                20,
                "Demo Teacher",
                datetime.now().isoformat(),
            ),
        )


# ============================================================
# DEMO QUIZZES
# ============================================================

def create_demo_quizzes():

    count = execute(
        "SELECT COUNT(*) AS c FROM quizzes",
        fetch=True,
    )[0]["c"]

    if count > 0:
        return

    questions = [
        {
            "question": "Which language is widely used for AI?",
            "options": [
                "Python",
                "HTML",
                "CSS",
                "SQL",
            ],
            "answer": "Python",
        },
        {
            "question": "What does AI stand for?",
            "options": [
                "Artificial Intelligence",
                "Automated Internet",
                "Advanced Input",
                "Application Interface",
            ],
            "answer": "Artificial Intelligence",
        },
    ]

    execute(
        """
        INSERT INTO quizzes
        (
            course,
            title,
            questions,
            duration,
            total_marks,
            teacher,
            created_at
        )
        VALUES (?,?,?,?,?,?,?)
        """,
        (
            "Artificial Intelligence",
            "AI Basics Quiz",
            json.dumps(questions),
            10,
            20,
            "Demo Teacher",
            datetime.now().isoformat(),
        ),
    )


# ============================================================
# OPENAI SETTINGS
# ============================================================

def get_api_key():

    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass

    return os.getenv("OPENAI_API_KEY")


def get_ai_mode():

    try:
        mode = st.secrets.get(
            "AI_MODE",
            "API",
        )
    except Exception:
        mode = os.getenv(
            "AI_MODE",
            "API",
        )

    return str(mode).upper()


def get_model():

    try:
        return st.secrets.get(
            "OPENAI_MODEL",
            "gpt-5.6",
        )
    except Exception:
        return os.getenv(
            "OPENAI_MODEL",
            "gpt-5.6",
        )


# ============================================================
# OPENAI REQUEST
# ============================================================

def ask_openai(
    prompt,
    system_prompt=(
        "You are Mohammad Ahmad, the Main AI Agent "
        "of PADHO PAKISTAN."
    ),
):

    api_key = get_api_key()

    if not api_key:

        return (
            "API key is not configured. "
            "Please add OPENAI_API_KEY to Streamlit Secrets."
        )

    if OpenAI is None:

        return (
            "OpenAI package is not installed. "
            "Run: pip install openai"
        )

    try:

        client = OpenAI(
            api_key=api_key
        )

        response = client.responses.create(
            model=get_model(),
            instructions=system_prompt,
            input=prompt,
        )

        return response.output_text

    except Exception as e:

        return f"OpenAI Error: {e}"


# ============================================================
# DEMO AI
# ============================================================

def demo_ai_response(prompt):

    prompt_lower = prompt.lower()

    if "assignment" in prompt_lower:
        return (
            "Mohammad Ahmad has routed your request to the "
            "Assignment Agent. Demo mode is active."
        )

    if "quiz" in prompt_lower:
        return (
            "Mohammad Ahmad has routed your request to the "
            "Quiz Agent. Demo mode is active."
        )

    if "attendance" in prompt_lower:
        return (
            "Mohammad Ahmad has routed your request to the "
            "Attendance Agent."
        )

    if "study" in prompt_lower:
        return (
            "Mohammad Ahmad has routed your request to the "
            "Personalized Learning Agent."
        )

    if "lesson" in prompt_lower:
        return (
            "Mohammad Ahmad has routed your request to the "
            "AI Lesson Planner Agent."
        )

    return (
        "Hello! I am Mohammad Ahmad, the Main AI Agent "
        "of PADHO PAKISTAN. Demo Mode is active. "
        "I can coordinate all 50 LMS agents."
    )


def ai_response(prompt):

    if get_ai_mode() == "DEMO":
        return demo_ai_response(prompt)

    return ask_openai(prompt)


# ============================================================
# AGENT ROUTER
# ============================================================

def route_agent(user_request):

    text = user_request.lower()

    rules = [
        (["student", "student profile"],
         "Student Management Agent"),

        (["teacher"],
         "Teacher Management Agent"),

        (["course"],
         "Course Management Agent"),

        (["subject"],
         "Subject Management Agent"),

        (["class", "section"],
         "Class Management Agent"),

        (["enroll"],
         "Enrollment Agent"),

        (["submit assignment", "submission"],
         "Assignment Submission Agent"),

        (["grade assignment", "mark assignment"],
         "Assignment Grading Agent"),

        (["assignment", "homework"],
         "Assignment Agent"),

        (["quiz result", "quiz score"],
         "Quiz Evaluation Agent"),

        (["quiz"],
         "Quiz Agent"),

        (["exam"],
         "Exam Management Agent"),

        (["question bank"],
         "Question Bank Agent"),

        (["generate question"],
         "AI Question Generator Agent"),

        (["attendance"],
         "Attendance Agent"),

        (["timetable", "schedule"],
         "Timetable Agent"),

        (["notes", "study material"],
         "Study Material Agent"),

        (["explain", "teach me"],
         "AI Tutor Agent"),

        (["lesson plan"],
         "AI Lesson Planner Agent"),

        (["curriculum", "clo", "plo"],
         "Curriculum Agent"),

        (["performance"],
         "Student Performance Agent"),

        (["personalized"],
         "Personalized Learning Agent"),

        (["study plan"],
         "Study Planner Agent"),

        (["reminder"],
         "Reminder Agent"),

        (["notification"],
         "Notification Agent"),

        (["certificate"],
         "Certificate Agent"),

        (["achievement", "badge"],
         "Achievement Agent"),

        (["career"],
         "Career Guidance Agent"),

        (["coding", "programming"],
         "Coding Practice Agent"),

        (["fyp", "final year project"],
         "Project/FYP Agent"),

        (["teacher assistant"],
         "Teacher Assistant Agent"),

        (["generate content", "notes generation"],
         "AI Content Generator Agent"),

        (["rubric"],
         "Rubric Agent"),

        (["feedback"],
         "Feedback Agent"),

        (["analytics"],
         "Analytics Agent"),

        (["dashboard"],
         "Dashboard Agent"),

        (["report"],
         "Report Generator Agent"),

        (["pdf"],
         "PDF Generator Agent"),

        (["word", "docx"],
         "Word Document Agent"),

        (["excel", "xlsx"],
         "Excel Agent"),

        (["announcement"],
         "Announcement Agent"),

        (["email"],
         "Email Agent"),

        (["discussion", "forum"],
         "Discussion Agent"),

        (["chatbot"],
         "Chatbot Agent"),

        (["search"],
         "Search Agent"),

        (["file", "upload"],
         "File Management Agent"),

        (["login", "password", "user id"],
         "Authentication Agent"),

        (["security"],
         "Security Agent"),

        (["database"],
         "Database Agent"),

        (["system", "settings"],
         "System Administration Agent"),
    ]

    for keywords, agent in rules:

        if any(
            keyword in text
            for keyword in keywords
        ):
            return agent

    return "Chatbot Agent"


# ============================================================
# AGENT LOGGING
# ============================================================

def log_agent_request(
    request,
    agent,
    status="Success",
):

    execute(
        """
        INSERT INTO agent_logs
        (
            username,
            role,
            request,
            selected_agent,
            status,
            created_at
        )
        VALUES (?,?,?,?,?,?)
        """,
        (
            st.session_state.get(
                "username",
                "",
            ),
            st.session_state.get(
                "role",
                "",
            ),
            request,
            agent,
            status,
            datetime.now().isoformat(),
        ),
    )


# ============================================================
# AUTHENTICATION
# ============================================================

def login():

    st.title("🇵🇰 PADHO PAKISTAN")

    st.subheader(
        "AI-Powered Learning Management System"
    )

    st.write(
        "### 🤖 Main AI Agent: Mohammad Ahmad"
    )

    st.info(
        "Authorized LMS users must use the User ID and "
        "Password allocated by the Administrator."
    )

    with st.expander(
        "Demo Login Accounts"
    ):

        st.write(
            "Admin: admin / admin123"
        )

        st.write(
            "Teacher: teacher / teacher123"
        )

        st.write(
            "Student: student / student123"
        )

    with st.form("login_form"):

        username = st.text_input(
            "🆔 User ID"
        )

        password = st.text_input(
            "🔐 Password",
            type="password",
        )

        submitted = st.form_submit_button(
            "🔐 Login",
            use_container_width=True,
            type="primary",
        )

        if submitted:

            user = execute(
                """
                SELECT *
                FROM users
                WHERE username=?
                AND password=?
                """,
                (
                    username.strip(),
                    hash_password(password),
                ),
                fetch=True,
            )

            if not user:

                st.error(
                    "Invalid User ID or Password."
                )

                return

            user = user[0]

            if user["status"] != "Active":

                st.error(
                    "🚫 Your LMS account is inactive. "
                    "Please contact the Administrator."
                )

                return

            st.session_state.logged_in = True
            st.session_state.username = user["username"]
            st.session_state.role = user["role"]
            st.session_state.user_id = user["id"]

            execute(
                """
                UPDATE users
                SET last_login=?
                WHERE id=?
                """,
                (
                    datetime.now().isoformat(),
                    user["id"],
                ),
            )

            st.success(
                "Login successful."
            )

            st.rerun()


# ============================================================
# ADMIN ACCESS CHECK
# ============================================================

def admin_only():

    if st.session_state.role != "Admin":

        st.error(
            "🚫 Administrator access required."
        )

        st.warning(
            "This area is restricted to authorized "
            "LMS administrators."
        )

        return False

    return True


# ============================================================
# SIDEBAR
# ============================================================

def sidebar():

    st.sidebar.title(
        "🇵🇰 PADHO PAKISTAN"
    )

    st.sidebar.caption(
        "Powered by Mohammad Ahmad"
    )

    if get_ai_mode() == "DEMO":

        st.sidebar.warning(
            "🟡 DEMO MODE"
        )

    else:

        if get_api_key():

            st.sidebar.success(
                "🟢 OPENAI API MODE"
            )

        else:

            st.sidebar.error(
                "🔴 API KEY NOT FOUND"
            )

    st.sidebar.divider()

    st.sidebar.write(
        f"👤 **{st.session_state.username}**"
    )

    st.sidebar.write(
        f"🔑 **{st.session_state.role}**"
    )

    st.sidebar.divider()

    common = [
        "Dashboard",
        "🤖 Mohammad Ahmad",
        "Assignments",
        "Submit Assignment",
        "Quizzes",
        "Attendance",
        "Results",
        "Study Materials",
        "Notifications",
        "AI Tutor",
    ]

    teacher_items = [
        "Manage Assignments",
        "Manage Quizzes",
        "Manage Attendance",
        "Students",
        "Course Management",
        "AI Lesson Planner",
        "Reports",
    ]

    admin_items = [
        "👑 Admin Panel",
        "Users",
        "Courses",
        "All Assignments",
        "All Results",
        "Agent Management",
        "Agent Logs",
        "System Settings",
        "Database",
    ]

    pages = common.copy()

    if st.session_state.role in [
        "Teacher",
        "Admin",
    ]:

        pages += teacher_items

    if st.session_state.role == "Admin":

        pages += admin_items

    pages += [
        "All 50 Agents",
        "Settings",
        "Logout",
    ]

    selected = st.sidebar.radio(
        "Navigation",
        pages,
    )

    st.session_state.page = selected


# ============================================================
# DASHBOARD
# ============================================================

def dashboard():

    st.title(
        "🏠 PADHO PAKISTAN Dashboard"
    )

    st.write(
        f"Welcome **{st.session_state.username}**"
    )

    st.caption(
        "Your intelligent education platform "
        "controlled by Mohammad Ahmad."
    )

    user_count = execute(
        "SELECT COUNT(*) c FROM users",
        fetch=True,
    )[0]["c"]

    active_users = execute(
        """
        SELECT COUNT(*) c
        FROM users
        WHERE status='Active'
        """,
        fetch=True,
    )[0]["c"]

    course_count = execute(
        "SELECT COUNT(*) c FROM courses",
        fetch=True,
    )[0]["c"]

    assignment_count = execute(
        "SELECT COUNT(*) c FROM assignments",
        fetch=True,
    )[0]["c"]

    quiz_count = execute(
        "SELECT COUNT(*) c FROM quizzes",
        fetch=True,
    )[0]["c"]

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "👥 Users",
        user_count,
    )

    c2.metric(
        "🟢 Active Users",
        active_users,
    )

    c3.metric(
        "📚 Courses",
        course_count,
    )

    c4.metric(
        "📝 Assignments",
        assignment_count,
    )

    c5.metric(
        "🧠 Quizzes",
        quiz_count,
    )

    st.divider()

    left, right = st.columns(2)

    with left:

        st.subheader(
            "🤖 Mohammad Ahmad"
        )

        st.info(
            "Main AI Agent is ready to coordinate "
            "all 50 specialized agents."
        )

        st.write(
            "Ask questions such as:"
        )

        st.write(
            "- Show my assignments\n"
            "- Create a Python quiz\n"
            "- Check attendance\n"
            "- Generate a lesson plan\n"
            "- Prepare a study plan\n"
            "- Generate performance report"
        )

    with right:

        st.subheader(
            "📢 Latest Announcements"
        )

        announcements = execute(
            """
            SELECT *
            FROM announcements
            ORDER BY id DESC
            LIMIT 5
            """,
            fetch=True,
        )

        if not announcements:

            st.info(
                "No announcements available."
            )

        for item in announcements:

            st.write(
                f"**{item['title']}**"
            )

            st.caption(
                item["message"]
            )


# ============================================================
# MOHAMMAD AHMAD
# ============================================================

def mohammad_ahmad():

    st.title(
        "🤖 MOHAMMAD AHMAD"
    )

    st.subheader(
        "Main AI LMS Agent"
    )

    st.info(
        "Mohammad Ahmad controls and coordinates "
        "all 50 PADHO PAKISTAN agents."
    )

    if st.session_state.chat_messages:

        for message in st.session_state.chat_messages:

            with st.chat_message(
                message["role"]
            ):

                st.write(
                    message["content"]
                )

    prompt = st.chat_input(
        "Ask Mohammad Ahmad anything about the LMS..."
    )

    if prompt:

        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        agent = route_agent(
            prompt
        )

        st.session_state.selected_agent = agent

        with st.spinner(
            f"🤖 Mohammad Ahmad → {agent}"
        ):

            response = ai_response(
                f"""
You are Mohammad Ahmad, the Main AI Agent
of PADHO PAKISTAN.

You coordinate 50 specialized LMS agents.

User role:
{st.session_state.role}

User:
{st.session_state.username}

Selected specialized agent:
{agent}

User request:
{prompt}

Respond professionally and helpfully.
"""
            )

        log_agent_request(
            prompt,
            agent,
            "Success",
        )

        final_response = (
            f"**🤖 Mohammad Ahmad**\n\n"
            f"**Selected Agent:** `{agent}`\n\n"
            f"{response}"
        )

        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": final_response,
            }
        )

        st.rerun()


# ============================================================
# ASSIGNMENTS
# ============================================================

def assignments():

    st.title(
        "📝 Assignments"
    )

    rows = execute(
        """
        SELECT
            assignments.id,
            assignments.title,
            courses.name AS course,
            assignments.description,
            assignments.due_date,
            assignments.total_marks,
            assignments.teacher
        FROM assignments
        LEFT JOIN courses
        ON assignments.course_id = courses.id
        ORDER BY assignments.id DESC
        """,
        fetch=True,
    )

    if not rows:

        st.info(
            "No assignments available."
        )

        return

    for item in rows:

        with st.expander(
            f"📝 {item['title']} — {item['course']}"
        ):

            st.write(
                item["description"]
            )

            c1, c2, c3 = st.columns(3)

            c1.write(
                f"📅 Due: {item['due_date']}"
            )

            c2.write(
                f"🎯 Marks: {item['total_marks']}"
            )

            c3.write(
                f"👨‍🏫 {item['teacher']}"
            )


# ============================================================
# SUBMIT ASSIGNMENT
# ============================================================

def submit_assignment():

    st.title(
        "📤 Submit Assignment"
    )

    assignments_data = execute(
        """
        SELECT id,title
        FROM assignments
        ORDER BY id DESC
        """,
        fetch=True,
    )

    if not assignments_data:

        st.warning(
            "No assignments available."
        )

        return

    options = {
        f"{x['id']} - {x['title']}": x["id"]
        for x in assignments_data
    }

    selected = st.selectbox(
        "Select Assignment",
        list(options.keys()),
    )

    assignment_id = options[selected]

    text = st.text_area(
        "Submission Text"
    )

    uploaded = st.file_uploader(
        "Upload Assignment",
        type=[
            "pdf",
            "docx",
            "doc",
            "txt",
            "py",
            "csv",
            "xlsx",
            "pptx",
        ],
    )

    if st.button(
        "📤 Submit Assignment",
        type="primary",
    ):

        file_name = ""

        if uploaded:

            safe_name = (
                f"{st.session_state.username}_"
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}_"
                f"{uploaded.name}"
            )

            path = UPLOAD_DIR / safe_name

            with open(
                path,
                "wb",
            ) as f:

                f.write(
                    uploaded.getbuffer()
                )

            file_name = safe_name

        execute(
            """
            INSERT INTO submissions
            (
                assignment_id,
                student,
                submission_text,
                file_name,
                submitted_at,
                status
            )
            VALUES (?,?,?,?,?,?)
            """,
            (
                assignment_id,
                st.session_state.username,
                text,
                file_name,
                datetime.now().isoformat(),
                "Submitted",
            ),
        )

        st.success(
            "Assignment submitted successfully."
        )


# ============================================================
# MANAGE ASSIGNMENTS
# ============================================================

def manage_assignments():

    st.title(
        "📝 Manage Assignments"
    )

    courses = execute(
        "SELECT id,name FROM courses",
        fetch=True,
    )

    if not courses:

        st.warning(
            "Create a course first."
        )

        return

    course_map = {
        x["name"]: x["id"]
        for x in courses
    }

    with st.form(
        "assignment_form"
    ):

        title = st.text_input(
            "Assignment Title"
        )

        course = st.selectbox(
            "Course",
            list(course_map.keys()),
        )

        description = st.text_area(
            "Instructions"
        )

        due = st.date_input(
            "Due Date"
        )

        marks = st.number_input(
            "Total Marks",
            min_value=1.0,
            value=20.0,
        )

        submit = st.form_submit_button(
            "Create Assignment"
        )

        if submit:

            if not title.strip():

                st.error(
                    "Assignment title is required."
                )

                return

            execute(
                """
                INSERT INTO assignments
                (
                    course_id,
                    title,
                    description,
                    due_date,
                    total_marks,
                    teacher,
                    created_at
                )
                VALUES (?,?,?,?,?,?,?)
                """,
                (
                    course_map[course],
                    title,
                    description,
                    str(due),
                    marks,
                    st.session_state.username,
                    datetime.now().isoformat(),
                ),
            )

            st.success(
                "Assignment created successfully."
            )


# ============================================================
# QUIZZES
# ============================================================

def quizzes():

    st.title(
        "🧠 Quizzes"
    )

    quiz_data = execute(
        """
        SELECT *
        FROM quizzes
        ORDER BY id DESC
        """,
        fetch=True,
    )

    if not quiz_data:

        st.info(
            "No quizzes available."
        )

        return

    for quiz in quiz_data:

        st.subheader(
            f"🧠 {quiz['title']}"
        )

        questions = json.loads(
            quiz["questions"]
        )

        answers = {}

        with st.form(
            f"quiz_{quiz['id']}"
        ):

            for i, question in enumerate(
                questions
            ):

                st.write(
                    f"**Q{i + 1}. "
                    f"{question['question']}**"
                )

                answers[i] = st.radio(
                    "Select answer",
                    question["options"],
                    key=f"{quiz['id']}_{i}",
                )

            submitted = st.form_submit_button(
                "Submit Quiz"
            )

            if submitted:

                score = 0

                for i, question in enumerate(
                    questions
                ):

                    if (
                        answers[i]
                        == question["answer"]
                    ):

                        score += 1

                percentage = (
                    score
                    / len(questions)
                    * 100
                )

                execute(
                    """
                    INSERT INTO quiz_attempts
                    (
                        quiz_id,
                        student,
                        score,
                        percentage,
                        submitted_at
                    )
                    VALUES (?,?,?,?,?)
                    """,
                    (
                        quiz["id"],
                        st.session_state.username,
                        score,
                        percentage,
                        datetime.now().isoformat(),
                    ),
                )

                st.success(
                    f"Quiz submitted. Score: "
                    f"{score}/{len(questions)} "
                    f"({percentage:.1f}%)"
                )


# ============================================================
# MANAGE QUIZZES
# ============================================================

def manage_quizzes():

    st.title(
        "🧠 Quiz Management"
    )

    with st.form(
        "quiz_form"
    ):

        title = st.text_input(
            "Quiz Title"
        )

        course = st.text_input(
            "Course",
            value="Python Programming",
        )

        duration = st.number_input(
            "Duration (minutes)",
            min_value=1,
            value=10,
        )

        q1 = st.text_input(
            "Question 1"
        )

        q1a = st.text_input(
            "Option A"
        )

        q1b = st.text_input(
            "Option B"
        )

        q1c = st.text_input(
            "Option C"
        )

        q1d = st.text_input(
            "Option D"
        )

        answer = st.selectbox(
            "Correct Answer",
            [
                q1a,
                q1b,
                q1c,
                q1d,
            ],
        )

        create = st.form_submit_button(
            "Create Quiz"
        )

        if create:

            if not title.strip():

                st.error(
                    "Quiz title is required."
                )

                return

            questions = [
                {
                    "question": q1,
                    "options": [
                        q1a,
                        q1b,
                        q1c,
                        q1d,
                    ],
                    "answer": answer,
                }
            ]

            execute(
                """
                INSERT INTO quizzes
                (
                    course,
                    title,
                    questions,
                    duration,
                    total_marks,
                    teacher,
                    created_at
                )
                VALUES (?,?,?,?,?,?,?)
                """,
                (
                    course,
                    title,
                    json.dumps(questions),
                    duration,
                    10,
                    st.session_state.username,
                    datetime.now().isoformat(),
                ),
            )

            st.success(
                "Quiz created successfully."
            )


# ============================================================
# ATTENDANCE
# ============================================================

def attendance():

    st.title(
        "📋 Attendance"
    )

    if st.session_state.role == "Student":

        records = execute(
            """
            SELECT
                course,
                SUM(
                    CASE
                    WHEN status='Present'
                    THEN 1
                    ELSE 0
                    END
                ) AS present,
                COUNT(*) AS total
            FROM attendance
            WHERE student=?
            GROUP BY course
            """,
            (
                st.session_state.username,
            ),
            fetch=True,
        )

        if not records:

            st.info(
                "No attendance records available."
            )

            return

        for row in records:

            percentage = (
                row["present"]
                / row["total"]
                * 100
            )

            st.metric(
                row["course"],
                f"{percentage:.1f}%",
            )

    else:

        st.subheader(
            "Mark Attendance"
        )

        students = execute(
            """
            SELECT username,name
            FROM users
            WHERE role='Student'
            AND status='Active'
            """,
            fetch=True,
        )

        courses = execute(
            "SELECT name FROM courses",
            fetch=True,
        )

        if students and courses:

            student = st.selectbox(
                "Student",
                [
                    x["username"]
                    for x in students
                ],
            )

            course = st.selectbox(
                "Course",
                [
                    x["name"]
                    for x in courses
                ],
            )

            status = st.selectbox(
                "Status",
                [
                    "Present",
                    "Absent",
                    "Late",
                    "Leave",
                ],
            )

            if st.button(
                "Save Attendance"
            ):

                execute(
                    """
                    INSERT INTO attendance
                    (
                        student,
                        course,
                        attendance_date,
                        status
                    )
                    VALUES (?,?,?,?)
                    """,
                    (
                        student,
                        course,
                        str(date.today()),
                        status,
                    ),
                )

                st.success(
                    "Attendance saved."
                )


# ============================================================
# RESULTS
# ============================================================

def results():

    st.title(
        "📊 Results"
    )

    if st.session_state.role == "Student":

        rows = execute(
            """
            SELECT
                course,
                marks,
                grade,
                grade_point,
                semester
            FROM results
            WHERE student=?
            """,
            (
                st.session_state.username,
            ),
            fetch=True,
        )

    else:

        rows = execute(
            """
            SELECT
                student,
                course,
                marks,
                grade,
                grade_point,
                semester
            FROM results
            """,
            fetch=True,
        )

    if not rows:

        st.info(
            "No results available."
        )

        return

    if pd:

        st.dataframe(
            pd.DataFrame(
                [dict(x) for x in rows]
            ),
            use_container_width=True,
        )

    else:

        st.write(
            [dict(x) for x in rows]
        )


# ============================================================
# STUDY MATERIALS
# ============================================================

def study_materials():

    st.title(
        "📖 Study Materials"
    )

    materials = execute(
        """
        SELECT *
        FROM materials
        ORDER BY id DESC
        """,
        fetch=True,
    )

    if not materials:

        st.info(
            "No study materials uploaded."
        )

    for material in materials:

        st.write(
            f"📄 **{material['title']}**"
        )

        st.caption(
            f"Course: {material['course']} | "
            f"Uploaded by: {material['uploaded_by']}"
        )


# ============================================================
# NOTIFICATIONS
# ============================================================

def notifications():

    st.title(
        "🔔 Notifications"
    )

    rows = execute(
        """
        SELECT *
        FROM notifications
        WHERE username=?
        ORDER BY id DESC
        """,
        (
            st.session_state.username,
        ),
        fetch=True,
    )

    if not rows:

        st.info(
            "No notifications."
        )

        return

    for row in rows:

        st.info(
            f"🔔 {row['message']}"
        )


# ============================================================
# AI TUTOR
# ============================================================

def ai_tutor():

    st.title(
        "🤖 AI Tutor"
    )

    topic = st.text_input(
        "What would you like to learn?"
    )

    level = st.selectbox(
        "Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced",
        ],
    )

    if st.button(
        "Teach Me",
        type="primary",
    ):

        if not topic.strip():

            st.warning(
                "Please enter a topic."
            )

            return

        with st.spinner(
            "AI Tutor is preparing your lesson..."
        ):

            response = ai_response(
                f"""
You are the AI Tutor Agent of PADHO PAKISTAN.

Teach the student about:

{topic}

Student level:
{level}

Provide:

1. Simple explanation
2. Example
3. Practical example
4. Short quiz
5. Key points
"""
            )

        st.markdown(
            response
        )


# ============================================================
# AI LESSON PLANNER
# ============================================================

def lesson_planner():

    st.title(
        "🧑‍🏫 AI Lesson Planner"
    )

    topic = st.text_input(
        "Lesson Topic"
    )

    duration = st.number_input(
        "Duration in minutes",
        15,
        180,
        60,
    )

    if st.button(
        "Generate Lesson Plan"
    ):

        response = ai_response(
            f"""
Create a detailed university-level lesson plan.

Topic:
{topic}

Duration:
{duration} minutes

Include:

Learning objectives
Introduction
Teaching activities
Examples
Student activity
Assessment
Homework
Learning outcomes
"""
        )

        st.markdown(
            response
        )


# ============================================================
# REPORTS
# ============================================================

def reports():

    st.title(
        "📄 Reports"
    )

    report_type = st.selectbox(
        "Report Type",
        [
            "Student Performance",
            "Attendance",
            "Assignments",
            "Quiz Results",
        ],
    )

    if st.button(
        "Generate Report"
    ):

        if report_type == "Assignments":

            rows = execute(
                "SELECT * FROM assignments",
                fetch=True,
            )

        elif report_type == "Quiz Results":

            rows = execute(
                "SELECT * FROM quiz_attempts",
                fetch=True,
            )

        elif report_type == "Attendance":

            rows = execute(
                "SELECT * FROM attendance",
                fetch=True,
            )

        else:

            rows = execute(
                "SELECT * FROM results",
                fetch=True,
            )

        if rows and pd:

            df = pd.DataFrame(
                [dict(x) for x in rows]
            )

            st.dataframe(
                df,
                use_container_width=True,
            )

            csv = df.to_csv(
                index=False
            ).encode(
                "utf-8"
            )

            st.download_button(
                "⬇️ Download CSV",
                csv,
                file_name=(
                    "padho_pakistan_report.csv"
                ),
                mime="text/csv",
            )


# ============================================================
# ADMIN PANEL
# ============================================================

def admin_panel():

    if not admin_only():
        return

    st.title(
        "👑 PADHO PAKISTAN ADMIN PANEL"
    )

    st.subheader(
        "🔐 LMS User Access Management"
    )

    st.info(
        "The Administrator controls who can access "
        "PADHO PAKISTAN. Create User IDs, allocate "
        "passwords, assign roles and control account status."
    )

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    total_users = execute(
        "SELECT COUNT(*) c FROM users",
        fetch=True,
    )[0]["c"]

    active_users = execute(
        """
        SELECT COUNT(*) c
        FROM users
        WHERE status='Active'
        """,
        fetch=True,
    )[0]["c"]

    inactive_users = execute(
        """
        SELECT COUNT(*) c
        FROM users
        WHERE status!='Active'
        """,
        fetch=True,
    )[0]["c"]

    students = execute(
        """
        SELECT COUNT(*) c
        FROM users
        WHERE role='Student'
        """,
        fetch=True,
    )[0]["c"]

    teachers = execute(
        """
        SELECT COUNT(*) c
        FROM users
        WHERE role='Teacher'
        """,
        fetch=True,
    )[0]["c"]

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Total Users",
        total_users,
    )

    c2.metric(
        "Active",
        active_users,
    )

    c3.metric(
        "Inactive",
        inactive_users,
    )

    c4.metric(
        "Students",
        students,
    )

    c5.metric(
        "Teachers",
        teachers,
    )

    st.divider()

    # --------------------------------------------------------
    # CREATE ACCOUNT
    # --------------------------------------------------------

    st.subheader(
        "➕ Allocate New LMS Account"
    )

    with st.form(
        "admin_create_user"
    ):

        col1, col2 = st.columns(2)

        with col1:

            new_username = st.text_input(
                "🆔 LMS User ID",
                placeholder="e.g. bilal001",
            )

            new_name = st.text_input(
                "👤 Full Name",
                placeholder="Enter user's full name",
            )

            new_email = st.text_input(
                "📧 Email",
                placeholder="user@example.com",
            )

            new_role = st.selectbox(
                "🔑 User Role",
                [
                    "Student",
                    "Teacher",
                    "Admin",
                ],
            )

        with col2:

            new_department = st.text_input(
                "🏢 Department",
                placeholder="Computer Science",
            )

            new_semester = st.text_input(
                "📚 Semester",
                placeholder="e.g. 5",
            )

            new_password = st.text_input(
                "🔐 Password",
                type="password",
                placeholder="Enter password",
            )

            auto_password = st.checkbox(
                "Generate secure password automatically",
                value=False,
            )

        create_account = st.form_submit_button(
            "➕ CREATE LMS ACCOUNT",
            type="primary",
            use_container_width=True,
        )

        if create_account:

            username = new_username.strip()
            password = new_password.strip()

            if not username:

                st.error(
                    "User ID is required."
                )

            elif not new_name.strip():

                st.error(
                    "Full Name is required."
                )

            else:

                if auto_password:
                    password = generate_password(12)

                if not password:

                    st.error(
                        "Password is required or enable "
                        "automatic password generation."
                    )

                else:

                    existing = execute(
                        """
                        SELECT id
                        FROM users
                        WHERE username=?
                        """,
                        (username,),
                        fetch=True,
                    )

                    if existing:

                        st.error(
                            "This User ID already exists."
                        )

                    else:

                        try:

                            execute(
                                """
                                INSERT INTO users
                                (
                                    username,
                                    password,
                                    name,
                                    role,
                                    email,
                                    department,
                                    semester,
                                    status,
                                    created_at
                                )
                                VALUES (?,?,?,?,?,?,?,?,?)
                                """,
                                (
                                    username,
                                    hash_password(
                                        password
                                    ),
                                    new_name.strip(),
                                    new_role,
                                    new_email.strip(),
                                    new_department.strip(),
                                    new_semester.strip(),
                                    "Active",
                                    datetime.now().isoformat(),
                                ),
                            )

                            st.success(
                                f"✅ LMS account created "
                                f"for {new_name}."
                            )

                            st.code(
                                f"User ID: {username}\n"
                                f"Password: {password}\n"
                                f"Role: {new_role}",
                                language="text",
                            )

                            st.warning(
                                "Give these credentials only "
                                "to the authorized user."
                            )

                        except Exception as e:

                            st.error(
                                f"Unable to create account: {e}"
                            )

    st.divider()

    # --------------------------------------------------------
    # SEARCH USERS
    # --------------------------------------------------------

    st.subheader(
        "🔎 Search LMS Users"
    )

    search = st.text_input(
        "Search by User ID, Name, Email or Department",
        placeholder="Type search text...",
    )

    if search.strip():

        search_value = f"%{search.strip()}%"

        users = execute(
            """
            SELECT *
            FROM users
            WHERE username LIKE ?
               OR name LIKE ?
               OR email LIKE ?
               OR department LIKE ?
            ORDER BY id DESC
            """,
            (
                search_value,
                search_value,
                search_value,
                search_value,
            ),
            fetch=True,
        )

    else:

        users = execute(
            """
            SELECT *
            FROM users
            ORDER BY id DESC
            """,
            fetch=True,
        )

    # --------------------------------------------------------
    # USER TABLE
    # --------------------------------------------------------

    st.subheader(
        "👥 LMS User Accounts"
    )

    if users and pd:

        display_data = []

        for user in users:

            display_data.append(
                {
                    "Database ID": user["id"],
                    "User ID": user["username"],
                    "Name": user["name"],
                    "Role": user["role"],
                    "Email": user["email"],
                    "Department": user["department"],
                    "Semester": user["semester"],
                    "Status": user["status"],
                    "Created": user["created_at"],
                    "Last Login": user["last_login"],
                }
            )

        st.dataframe(
            pd.DataFrame(display_data),
            use_container_width=True,
            hide_index=True,
        )

    elif users:

        for user in users:

            st.write(
                user["username"],
                user["name"],
                user["role"],
                user["status"],
            )

    else:

        st.info(
            "No users found."
        )

    st.divider()

    # --------------------------------------------------------
    # MANAGE EXISTING ACCOUNT
    # --------------------------------------------------------

    st.subheader(
        "🛠️ Manage Existing LMS Account"
    )

    if not users:

        st.info(
            "No accounts available."
        )

        return

    user_options = {
        f"{u['username']} — "
        f"{u['name']} — "
        f"{u['role']} — "
        f"{u['status']}": u["id"]
        for u in users
    }

    selected_label = st.selectbox(
        "Select User Account",
        list(user_options.keys()),
    )

    selected_id = user_options[
        selected_label
    ]

    selected_user_rows = execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (selected_id,),
        fetch=True,
    )

    if not selected_user_rows:
        return

    selected_user = selected_user_rows[0]

    st.write(
        f"### 👤 {selected_user['name']}"
    )

    info1, info2, info3, info4 = st.columns(4)

    info1.metric(
        "User ID",
        selected_user["username"],
    )

    info2.metric(
        "Role",
        selected_user["role"],
    )

    info3.metric(
        "Status",
        selected_user["status"],
    )

    info4.metric(
        "Database ID",
        selected_user["id"],
    )

    # --------------------------------------------------------
    # ACCOUNT ACTIONS
    # --------------------------------------------------------

    tab1, tab2, tab3 = st.tabs(
        [
            "🔐 Password",
            "⚙️ Account Settings",
            "🗑️ Delete",
        ]
    )

    # --------------------------------------------------------
    # PASSWORD
    # --------------------------------------------------------

    with tab1:

        st.write(
            "### 🔐 Reset / Allocate Password"
        )

        with st.form(
            "reset_password_form"
        ):

            password1 = st.text_input(
                "New Password",
                type="password",
            )

            password2 = st.text_input(
                "Confirm New Password",
                type="password",
            )

            generate_new = st.checkbox(
                "Generate secure password automatically"
            )

            reset_password = st.form_submit_button(
                "🔐 RESET PASSWORD",
                type="primary",
            )

            if reset_password:

                if generate_new:

                    final_password = generate_password(
                        12
                    )

                else:

                    final_password = password1.strip()

                    if not final_password:

                        st.error(
                            "Enter a password."
                        )

                        st.stop()

                    if final_password != password2:

                        st.error(
                            "Passwords do not match."
                        )

                        st.stop()

                execute(
                    """
                    UPDATE users
                    SET password=?
                    WHERE id=?
                    """,
                    (
                        hash_password(
                            final_password
                        ),
                        selected_user["id"],
                    ),
                )

                st.success(
                    "Password successfully updated."
                )

                st.code(
                    f"User ID: "
                    f"{selected_user['username']}\n"
                    f"New Password: "
                    f"{final_password}",
                    language="text",
                )

    # --------------------------------------------------------
    # ACCOUNT SETTINGS
    # --------------------------------------------------------

    with tab2:

        st.write(
            "### ⚙️ Account Settings"
        )

        with st.form(
            "account_settings_form"
        ):

            updated_name = st.text_input(
                "Full Name",
                value=selected_user["name"],
            )

            updated_email = st.text_input(
                "Email",
                value=selected_user["email"] or "",
            )

            updated_role = st.selectbox(
                "Role",
                [
                    "Student",
                    "Teacher",
                    "Admin",
                ],
                index=[
                    "Student",
                    "Teacher",
                    "Admin",
                ].index(
                    selected_user["role"]
                ),
            )

            updated_department = st.text_input(
                "Department",
                value=(
                    selected_user["department"]
                    or ""
                ),
            )

            updated_semester = st.text_input(
                "Semester",
                value=(
                    selected_user["semester"]
                    or ""
                ),
            )

            updated_status = st.selectbox(
                "Account Status",
                [
                    "Active",
                    "Inactive",
                ],
                index=(
                    0
                    if selected_user["status"]
                    == "Active"
                    else 1
                ),
            )

            save_changes = st.form_submit_button(
                "💾 SAVE ACCOUNT SETTINGS",
                type="primary",
            )

            if save_changes:

                # Prevent accidental removal of current admin
                if (
                    selected_user["id"]
                    == st.session_state.user_id
                    and updated_status
                    != "Active"
                ):

                    st.error(
                        "You cannot deactivate your own "
                        "currently logged-in administrator account."
                    )

                else:

                    execute(
                        """
                        UPDATE users
                        SET
                            name=?,
                            email=?,
                            role=?,
                            department=?,
                            semester=?,
                            status=?
                        WHERE id=?
                        """,
                        (
                            updated_name.strip(),
                            updated_email.strip(),
                            updated_role,
                            updated_department.strip(),
                            updated_semester.strip(),
                            updated_status,
                            selected_user["id"],
                        ),
                    )

                    st.success(
                        "Account settings updated."
                    )

    # --------------------------------------------------------
    # DELETE ACCOUNT
    # --------------------------------------------------------

    with tab3:

        st.write(
            "### 🗑️ Delete LMS Account"
        )

        st.warning(
            "Deleting an account is permanent. "
            "The user's academic records may still reference "
            "the User ID."
        )

        confirm_delete = st.checkbox(
            "I understand that this account will be permanently deleted."
        )

        if st.button(
            "🗑️ DELETE ACCOUNT",
            type="secondary",
        ):

            if not confirm_delete:

                st.error(
                    "Please confirm deletion first."
                )

            elif (
                selected_user["id"]
                == st.session_state.user_id
            ):

                st.error(
                    "You cannot delete your own "
                    "currently logged-in account."
                )

            else:

                execute(
                    """
                    DELETE FROM users
                    WHERE id=?
                    """,
                    (
                        selected_user["id"],
                    ),
                )

                st.success(
                    "LMS account deleted."
                )

                st.rerun()

    st.divider()

    # --------------------------------------------------------
    # QUICK ACCOUNT CONTROL
    # --------------------------------------------------------

    st.subheader(
        "⚡ Quick Account Control"
    )

    quick1, quick2, quick3 = st.columns(3)

    with quick1:

        if st.button(
            "🟢 Activate Account",
            use_container_width=True,
        ):

            execute(
                """
                UPDATE users
                SET status='Active'
                WHERE id=?
                """,
                (
                    selected_user["id"],
                ),
            )

            st.success(
                "Account activated."
            )

            st.rerun()

    with quick2:

        if st.button(
            "🔴 Deactivate Account",
            use_container_width=True,
        ):

            if (
                selected_user["id"]
                == st.session_state.user_id
            ):

                st.error(
                    "You cannot deactivate yourself."
                )

            else:

                execute(
                    """
                    UPDATE users
                    SET status='Inactive'
                    WHERE id=?
                    """,
                    (
                        selected_user["id"],
                    ),
                )

                st.success(
                    "Account deactivated."
                )

                st.rerun()

    with quick3:

        if st.button(
            "🔄 Generate Password",
            use_container_width=True,
        ):

            new_password = generate_password(
                12
            )

            execute(
                """
                UPDATE users
                SET password=?
                WHERE id=?
                """,
                (
                    hash_password(
                        new_password
                    ),
                    selected_user["id"],
                ),
            )

            st.success(
                "New password generated."
            )

            st.code(
                f"User ID: "
                f"{selected_user['username']}\n"
                f"Password: "
                f"{new_password}",
                language="text",
            )


# ============================================================
# ALL 50 AGENTS
# ============================================================

def all_agents():

    st.title(
        "🤖 PADHO PAKISTAN — 50 AI AGENTS"
    )

    st.write(
        "All specialized agents are controlled by "
        "**Mohammad Ahmad — Main AI Agent**."
    )

    for agent_id, name, category in AGENTS:

        with st.expander(
            f"{agent_id}. {name}"
        ):

            st.write(
                f"**Category:** {category}"
            )

            st.write(
                AGENT_DESCRIPTIONS[name]
            )

            if st.button(
                f"Open {name}",
                key=f"agent_{agent_id}",
            ):

                st.session_state.selected_agent = name

                st.success(
                    f"{name} selected by Mohammad Ahmad."
                )

    if st.session_state.selected_agent:

        st.divider()

        st.subheader(
            "Selected Agent"
        )

        st.info(
            st.session_state.selected_agent
        )

        request = st.text_area(
            "Give this agent a task"
        )

        if st.button(
            "▶️ Run Agent"
        ):

            response = ai_response(
                f"""
You are the specialized agent:

{st.session_state.selected_agent}

You operate under Mohammad Ahmad,
the Main Agent of PADHO PAKISTAN.

User role:
{st.session_state.role}

Task:
{request}
"""
            )

            log_agent_request(
                request,
                st.session_state.selected_agent,
            )

            st.markdown(
                response
            )


# ============================================================
# AGENT MANAGEMENT
# ============================================================

def agent_management():

    if not admin_only():
        return

    st.title(
        "⚙️ Agent Management"
    )

    data = []

    for agent_id, name, category in AGENTS:

        data.append(
            {
                "ID": agent_id,
                "Agent": name,
                "Category": category,
                "Status": "🟢 Active",
                "Controller": "Mohammad Ahmad",
            }
        )

    if pd:

        st.dataframe(
            pd.DataFrame(data),
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# AGENT LOGS
# ============================================================

def agent_logs():

    if not admin_only():
        return

    st.title(
        "📜 Agent Activity Logs"
    )

    rows = execute(
        """
        SELECT *
        FROM agent_logs
        ORDER BY id DESC
        LIMIT 200
        """,
        fetch=True,
    )

    if not rows:

        st.info(
            "No agent activity yet."
        )

        return

    if pd:

        st.dataframe(
            pd.DataFrame(
                [dict(x) for x in rows]
            ),
            use_container_width=True,
        )


# ============================================================
# USERS
# ============================================================

def users_page():

    if not admin_only():
        return

    st.title(
        "👥 User Management"
    )

    rows = execute(
        """
        SELECT
            id,
            username,
            name,
            role,
            email,
            department,
            semester,
            status,
            created_at,
            last_login
        FROM users
        ORDER BY id DESC
        """,
        fetch=True,
    )

    if pd:

        st.dataframe(
            pd.DataFrame(
                [dict(x) for x in rows]
            ),
            use_container_width=True,
        )

    st.info(
        "For complete account allocation and password "
        "management, use the 👑 Admin Panel."
    )


# ============================================================
# COURSE MANAGEMENT
# ============================================================

def course_management():

    if st.session_state.role not in [
        "Admin",
        "Teacher",
    ]:

        st.error(
            "Access denied."
        )

        return

    st.title(
        "📚 Course Management"
    )

    rows = execute(
        "SELECT * FROM courses",
        fetch=True,
    )

    if pd:

        st.dataframe(
            pd.DataFrame(
                [dict(x) for x in rows]
            ),
            use_container_width=True,
        )

    st.divider()

    with st.form(
        "course_form"
    ):

        code = st.text_input(
            "Course Code"
        )

        name = st.text_input(
            "Course Name"
        )

        department = st.text_input(
            "Department"
        )

        credit = st.number_input(
            "Credit Hours",
            1,
            6,
            3,
        )

        teacher = st.text_input(
            "Teacher"
        )

        description = st.text_area(
            "Description"
        )

        create = st.form_submit_button(
            "Create Course"
        )

        if create:

            execute(
                """
                INSERT INTO courses
                (
                    code,
                    name,
                    department,
                    credit_hours,
                    teacher,
                    description
                )
                VALUES (?,?,?,?,?,?)
                """,
                (
                    code,
                    name,
                    department,
                    credit,
                    teacher,
                    description,
                ),
            )

            st.success(
                "Course created successfully."
            )


# ============================================================
# DATABASE
# ============================================================

def database_page():

    if not admin_only():
        return

    st.title(
        "💾 Database Administration"
    )

    st.write(
        f"Database: `{DB_PATH}`"
    )

    tables = [
        "users",
        "courses",
        "assignments",
        "submissions",
        "quizzes",
        "quiz_attempts",
        "attendance",
        "results",
        "materials",
        "notifications",
        "announcements",
        "agent_logs",
    ]

    for table in tables:

        count = execute(
            f"""
            SELECT COUNT(*) AS c
            FROM {table}
            """,
            fetch=True,
        )[0]["c"]

        st.write(
            f"**{table}:** {count} records"
        )


# ============================================================
# SETTINGS
# ============================================================

def settings_page():

    st.title(
        "⚙️ PADHO PAKISTAN Settings"
    )

    st.subheader(
        "🔐 OpenAI API Configuration"
    )

    st.info(
        "The API key is read from Streamlit Secrets "
        "and is never displayed."
    )

    if get_api_key():

        st.success(
            "🟢 OPENAI_API_KEY detected."
        )

    else:

        st.error(
            "🔴 OPENAI_API_KEY not found."
        )

    st.write(
        f"**AI Mode:** {get_ai_mode()}"
    )

    st.write(
        f"**Model:** {get_model()}"
    )

    st.divider()

    st.subheader(
        "🇵🇰 Application"
    )

    st.write(
        "**Name:** PADHO PAKISTAN"
    )

    st.write(
        "**Main Agent:** Mohammad Ahmad"
    )

    st.write(
        "**Specialized Agents:** 50"
    )

    st.write(
        "**Database:** SQLite"
    )

    st.divider()

    st.subheader(
        "🧪 Test AI"
    )

    prompt = st.text_input(
        "Test prompt"
    )

    if st.button(
        "Test Mohammad Ahmad"
    ):

        response = ai_response(
            prompt or "Introduce yourself."
        )

        st.write(
            response
        )


# ============================================================
# LOGOUT
# ============================================================

def logout():

    st.session_state.clear()

    st.rerun()


# ============================================================
# MAIN ROUTER
# ============================================================

def main():

    init_db()

    if not st.session_state.logged_in:

        login()

        return

    sidebar()

    page = st.session_state.page

    if page == "Dashboard":

        dashboard()

    elif page == "🤖 Mohammad Ahmad":

        mohammad_ahmad()

    elif page == "Assignments":

        assignments()

    elif page == "Submit Assignment":

        submit_assignment()

    elif page == "Quizzes":

        quizzes()

    elif page == "Attendance":

        attendance()

    elif page == "Results":

        results()

    elif page == "Study Materials":

        study_materials()

    elif page == "Notifications":

        notifications()

    elif page == "AI Tutor":

        ai_tutor()

    elif page == "Manage Assignments":

        manage_assignments()

    elif page == "Manage Quizzes":

        manage_quizzes()

    elif page == "Manage Attendance":

        attendance()

    elif page == "Students":

        users_page()

    elif page == "Course Management":

        course_management()

    elif page == "AI Lesson Planner":

        lesson_planner()

    elif page == "Reports":

        reports()

    elif page == "👑 Admin Panel":

        admin_panel()

    elif page == "Users":

        users_page()

    elif page == "Courses":

        course_management()

    elif page == "All Assignments":

        assignments()

    elif page == "All Results":

        results()

    elif page == "Agent Management":

        agent_management()

    elif page == "Agent Logs":

        agent_logs()

    elif page == "System Settings":

        settings_page()

    elif page == "Database":

        database_page()

    elif page == "All 50 Agents":

        all_agents()

    elif page == "Settings":

        settings_page()

    elif page == "Logout":

        logout()

    else:

        dashboard()

    st.divider()

    st.caption(
        "🇵🇰 PADHO PAKISTAN | "
        "Main AI Agent: Mohammad Ahmad | "
        "50 Specialized Agents | "
        "Developed by Engr. Bilal Mehmood"
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    main()
