import os
import sqlite3
import hashlib
import json
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
# APPLICATION PATHS
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


# ============================================================
# AGENT DESCRIPTIONS
# ============================================================

AGENT_DESCRIPTIONS = {
    name: f"{name} handles {category.lower()} related LMS activities."
    for _, name, category in AGENTS
}


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "logged_in": False,
    "username": "",
    "role": "",
    "user_id": None,
    "page": "Dashboard",
    "selected_agent": None,
    "chat_messages": [],
}

for key, value in defaults.items():
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
            created_at TEXT
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

    conn.commit()
    conn.close()

    create_demo_users()
    create_demo_courses()
    create_demo_assignments()
    create_demo_quizzes()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


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
                (username,password,name,role,email,department,semester,created_at)
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    user[0],
                    hash_password(user[1]),
                    user[2],
                    user[3],
                    user[4],
                    user[5],
                    user[6],
                    datetime.now().isoformat(),
                ),
            )


def create_demo_courses():

    count = execute(
        "SELECT COUNT(*) AS c FROM courses",
        fetch=True,
    )[0]["c"]

    if count > 0:
        return

    courses = [
        ("AI101", "Artificial Intelligence", "Computer Science", 3),
        ("PY101", "Python Programming", "Computer Science", 3),
        ("DS101", "Data Science", "Computer Science", 3),
        ("ML101", "Machine Learning", "Computer Science", 3),
        ("WEB101", "Web Development", "Computer Science", 3),
    ]

    for code, name, dept, credit in courses:
        execute(
            """
            INSERT INTO courses
            (code,name,department,credit_hours,teacher,description)
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
            (course_id,title,description,due_date,total_marks,teacher,created_at)
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
            "options": ["Python", "HTML", "CSS", "SQL"],
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
        (course,title,questions,duration,total_marks,teacher,created_at)
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
# OPENAI
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
        mode = st.secrets.get("AI_MODE", "API")
    except Exception:
        mode = os.getenv("AI_MODE", "API")

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


def ask_openai(prompt, system_prompt="You are Mohammad Ahmad, the main AI agent of Padho Pakistan."):

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
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model=get_model(),
            instructions=system_prompt,
            input=prompt,
        )

        return response.output_text

    except Exception as e:
        return f"OpenAI Error: {e}"


def ai_response(prompt):

    mode = get_ai_mode()

    if mode == "DEMO":
        return demo_ai_response(prompt)

    return ask_openai(prompt)


def demo_ai_response(prompt):

    prompt_lower = prompt.lower()

    if "assignment" in prompt_lower:
        return (
            "Mohammad Ahmad has routed your request to the "
            "Assignment Agent. Demo mode: assignment services are ready."
        )

    if "quiz" in prompt_lower:
        return (
            "Mohammad Ahmad has routed your request to the "
            "Quiz Agent. Demo mode: quiz generation is available."
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
        "Hello! I am Mohammad Ahmad, the Main AI Agent of "
        "PADHO PAKISTAN. Demo Mode is active. "
        "I can coordinate the 50 LMS agents."
    )


# ============================================================
# MAIN AGENT ROUTER
# ============================================================

def route_agent(user_request):

    text = user_request.lower()

    rules = [
        (["student", "student profile"], "Student Management Agent"),
        (["teacher"], "Teacher Management Agent"),
        (["course"], "Course Management Agent"),
        (["subject"], "Subject Management Agent"),
        (["class", "section"], "Class Management Agent"),
        (["enroll"], "Enrollment Agent"),
        (["assignment", "homework"], "Assignment Agent"),
        (["submit assignment", "submission"], "Assignment Submission Agent"),
        (["grade assignment", "mark assignment"], "Assignment Grading Agent"),
        (["quiz"], "Quiz Agent"),
        (["quiz result", "quiz score"], "Quiz Evaluation Agent"),
        (["exam"], "Exam Management Agent"),
        (["question bank"], "Question Bank Agent"),
        (["generate question"], "AI Question Generator Agent"),
        (["attendance"], "Attendance Agent"),
        (["timetable", "schedule"], "Timetable Agent"),
        (["notes", "study material"], "Study Material Agent"),
        (["explain", "teach me"], "AI Tutor Agent"),
        (["lesson plan"], "AI Lesson Planner Agent"),
        (["curriculum", "clo", "plo"], "Curriculum Agent"),
        (["performance"], "Student Performance Agent"),
        (["personalized"], "Personalized Learning Agent"),
        (["study plan"], "Study Planner Agent"),
        (["reminder"], "Reminder Agent"),
        (["notification"], "Notification Agent"),
        (["certificate"], "Certificate Agent"),
        (["achievement", "badge"], "Achievement Agent"),
        (["career"], "Career Guidance Agent"),
        (["coding", "programming"], "Coding Practice Agent"),
        (["fyp", "final year project"], "Project/FYP Agent"),
        (["teacher assistant"], "Teacher Assistant Agent"),
        (["generate content", "notes generation"], "AI Content Generator Agent"),
        (["rubric"], "Rubric Agent"),
        (["feedback"], "Feedback Agent"),
        (["analytics"], "Analytics Agent"),
        (["dashboard"], "Dashboard Agent"),
        (["report"], "Report Generator Agent"),
        (["pdf"], "PDF Generator Agent"),
        (["word", "docx"], "Word Document Agent"),
        (["excel", "xlsx"], "Excel Agent"),
        (["announcement"], "Announcement Agent"),
        (["email"], "Email Agent"),
        (["discussion", "forum"], "Discussion Agent"),
        (["chatbot"], "Chatbot Agent"),
        (["search"], "Search Agent"),
        (["file", "upload"], "File Management Agent"),
        (["login", "password"], "Authentication Agent"),
        (["security"], "Security Agent"),
        (["database"], "Database Agent"),
        (["system", "settings"], "System Administration Agent"),
    ]

    for keywords, agent in rules:
        if any(keyword in text for keyword in keywords):
            return agent

    return "Chatbot Agent"


def log_agent_request(request, agent, status="Success"):

    execute(
        """
        INSERT INTO agent_logs
        (username,role,request,selected_agent,status,created_at)
        VALUES (?,?,?,?,?,?)
        """,
        (
            st.session_state.get("username", ""),
            st.session_state.get("role", ""),
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
    st.subheader("AI-Powered Learning Management System")
    st.write("### 🤖 Main AI Agent: Mohammad Ahmad")

    st.info(
        "Demo accounts: admin/admin123 | "
        "teacher/teacher123 | student/student123"
    )

    with st.form("login_form"):

        username = st.text_input("Username")
        password = st.text_input(
            "Password",
            type="password",
        )

        submitted = st.form_submit_button(
            "🔐 Login",
            use_container_width=True,
        )

        if submitted:

            user = execute(
                """
                SELECT * FROM users
                WHERE username=? AND password=?
                """,
                (
                    username,
                    hash_password(password),
                ),
                fetch=True,
            )

            if user:

                user = user[0]

                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.session_state.role = user["role"]
                st.session_state.user_id = user["id"]

                st.success("Login successful.")
                st.rerun()

            else:
                st.error("Invalid username or password.")


# ============================================================
# SIDEBAR
# ============================================================

def sidebar():

    st.sidebar.title("🇵🇰 PADHO PAKISTAN")
    st.sidebar.caption("Powered by Mohammad Ahmad")

    mode = get_ai_mode()

    if mode == "DEMO":
        st.sidebar.warning("🟡 DEMO MODE")
    else:
        if get_api_key():
            st.sidebar.success("🟢 OPENAI API MODE")
        else:
            st.sidebar.error("🔴 API KEY NOT FOUND")

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

    if st.session_state.role in ["Teacher", "Admin"]:
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

    st.title("🏠 PADHO PAKISTAN Dashboard")

    st.write(
        f"Welcome **{st.session_state.username}**"
    )

    st.caption(
        "Your intelligent education platform controlled by Mohammad Ahmad."
    )

    user_count = execute(
        "SELECT COUNT(*) c FROM users",
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

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("👥 Users", user_count)
    c2.metric("📚 Courses", course_count)
    c3.metric("📝 Assignments", assignment_count)
    c4.metric("🧠 Quizzes", quiz_count)

    st.divider()

    left, right = st.columns(2)

    with left:

        st.subheader("🤖 Mohammad Ahmad")

        st.info(
            "Main AI Agent is ready to coordinate all 50 specialized agents."
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

        st.subheader("📢 Latest Announcements")

        announcements = execute(
            """
            SELECT * FROM announcements
            ORDER BY id DESC LIMIT 5
            """,
            fetch=True,
        )

        if not announcements:
            st.info("No announcements available.")

        for item in announcements:
            st.write(
                f"**{item['title']}**"
            )
            st.caption(item["message"])


# ============================================================
# MOHAMMAD AHMAD AI
# ============================================================

def mohammad_ahmad():

    st.title("🤖 MOHAMMAD AHMAD")
    st.subheader("Main AI LMS Agent")

    st.info(
        "Mohammad Ahmad controls and coordinates all 50 PADHO PAKISTAN agents."
    )

    if st.session_state.chat_messages:

        for message in st.session_state.chat_messages:

            with st.chat_message(message["role"]):
                st.write(message["content"])

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

        agent = route_agent(prompt)

        st.session_state.selected_agent = agent

        with st.spinner(
            f"🤖 Mohammad Ahmad → {agent}"
        ):

            response = ai_response(
                f"""
You are Mohammad Ahmad, the Main AI Agent of PADHO PAKISTAN.

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

    st.title("📝 Assignments")

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
        st.info("No assignments available.")
        return

    for item in rows:

        with st.expander(
            f"📝 {item['title']} — {item['course']}"
        ):

            st.write(item["description"])

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

    st.title("📤 Submit Assignment")

    assignments_data = execute(
        "SELECT id,title FROM assignments ORDER BY id DESC",
        fetch=True,
    )

    if not assignments_data:
        st.warning("No assignments available.")
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

            with open(path, "wb") as f:
                f.write(uploaded.getbuffer())

            file_name = safe_name

        execute(
            """
            INSERT INTO submissions
            (assignment_id,student,submission_text,file_name,
             submitted_at,status)
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

        st.success("Assignment submitted successfully.")


# ============================================================
# MANAGE ASSIGNMENTS
# ============================================================

def manage_assignments():

    st.title("📝 Manage Assignments")

    courses = execute(
        "SELECT id,name FROM courses",
        fetch=True,
    )

    course_map = {
        x["name"]: x["id"]
        for x in courses
    }

    with st.form("assignment_form"):

        title = st.text_input("Assignment Title")

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

            execute(
                """
                INSERT INTO assignments
                (course_id,title,description,due_date,
                 total_marks,teacher,created_at)
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

            st.success("Assignment created successfully.")


# ============================================================
# QUIZZES
# ============================================================

def quizzes():

    st.title("🧠 Quizzes")

    quiz_data = execute(
        "SELECT * FROM quizzes ORDER BY id DESC",
        fetch=True,
    )

    if not quiz_data:
        st.info("No quizzes available.")
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
                    f"**Q{i + 1}. {question['question']}**"
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
                    score / len(questions) * 100
                )

                execute(
                    """
                    INSERT INTO quiz_attempts
                    (quiz_id,student,score,percentage,submitted_at)
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

    st.title("🧠 Quiz Management")

    with st.form("quiz_form"):

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
            [q1a, q1b, q1c, q1d],
        )

        create = st.form_submit_button(
            "Create Quiz"
        )

        if create:

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
                (course,title,questions,duration,
                 total_marks,teacher,created_at)
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

            st.success("Quiz created successfully.")


# ============================================================
# ATTENDANCE
# ============================================================

def attendance():

    st.title("📋 Attendance")

    if st.session_state.role == "Student":

        records = execute(
            """
            SELECT course,
                   SUM(CASE WHEN status='Present'
                       THEN 1 ELSE 0 END) AS present,
                   COUNT(*) AS total
            FROM attendance
            WHERE student=?
            GROUP BY course
            """,
            (st.session_state.username,),
            fetch=True,
        )

        if not records:

            st.info(
                "No attendance records available."
            )

            return

        for row in records:

            percentage = (
                row["present"] /
                row["total"] *
                100
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
                    (student,course,attendance_date,status)
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

    st.title("📊 Results")

    if st.session_state.role == "Student":

        rows = execute(
            """
            SELECT course,marks,grade,
                   grade_point,semester
            FROM results
            WHERE student=?
            """,
            (st.session_state.username,),
            fetch=True,
        )

    else:

        rows = execute(
            """
            SELECT student,course,marks,
                   grade,grade_point,semester
            FROM results
            """,
            fetch=True,
        )

    if not rows:
        st.info("No results available.")
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

    st.title("📖 Study Materials")

    materials = execute(
        """
        SELECT * FROM materials
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

    st.title("🔔 Notifications")

    rows = execute(
        """
        SELECT * FROM notifications
        WHERE username=?
        ORDER BY id DESC
        """,
        (st.session_state.username,),
        fetch=True,
    )

    if not rows:
        st.info("No notifications.")
        return

    for row in rows:

        st.info(
            f"🔔 {row['message']}"
        )


# ============================================================
# AI TUTOR
# ============================================================

def ai_tutor():

    st.title("🤖 AI Tutor")

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

        st.markdown(response)


# ============================================================
# AI LESSON PLANNER
# ============================================================

def lesson_planner():

    st.title("🧑‍🏫 AI Lesson Planner")

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

Topic: {topic}
Duration: {duration} minutes

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

        st.markdown(response)


# ============================================================
# REPORTS
# ============================================================

def reports():

    st.title("📄 Reports")

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
            ).encode("utf-8")

            st.download_button(
                "⬇️ Download CSV",
                csv,
                file_name="padho_pakistan_report.csv",
                mime="text/csv",
            )


# ============================================================
# ALL 50 AGENTS
# ============================================================

def all_agents():

    st.title("🤖 PADHO PAKISTAN — 50 AI AGENTS")

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

            st.markdown(response)


# ============================================================
# AGENT MANAGEMENT
# ============================================================

def agent_management():

    st.title("⚙️ Agent Management")

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

    st.title("📜 Agent Activity Logs")

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
        st.info("No agent activity yet.")
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

    st.title("👥 User Management")

    rows = execute(
        """
        SELECT id,username,name,role,email,
               department,semester,created_at
        FROM users
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

    st.divider()

    st.subheader(
        "Create User"
    )

    with st.form("create_user"):

        username = st.text_input(
            "Username"
        )

        name = st.text_input(
            "Full Name"
        )

        password = st.text_input(
            "Password",
            type="password",
        )

        role = st.selectbox(
            "Role",
            [
                "Student",
                "Teacher",
                "Admin",
            ],
        )

        email = st.text_input(
            "Email"
        )

        department = st.text_input(
            "Department"
        )

        create = st.form_submit_button(
            "Create User"
        )

        if create:

            try:

                execute(
                    """
                    INSERT INTO users
                    (username,password,name,role,email,
                     department,created_at)
                    VALUES (?,?,?,?,?,?,?)
                    """,
                    (
                        username,
                        hash_password(password),
                        name,
                        role,
                        email,
                        department,
                        datetime.now().isoformat(),
                    ),
                )

                st.success(
                    "User created."
                )

            except Exception as e:

                st.error(
                    f"Unable to create user: {e}"
                )


# ============================================================
# COURSE MANAGEMENT
# ============================================================

def course_management():

    st.title("📚 Course Management")

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

    with st.form("course_form"):

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
                (code,name,department,credit_hours,
                 teacher,description)
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
# DATABASE PAGE
# ============================================================

def database_page():

    st.title("💾 Database")

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
            f"SELECT COUNT(*) AS c FROM {table}",
            fetch=True,
        )[0]["c"]

        st.write(
            f"**{table}:** {count} records"
        )


# ============================================================
# SETTINGS
# ============================================================

def settings_page():

    st.title("⚙️ PADHO PAKISTAN Settings")

    st.subheader(
        "🔐 OpenAI API Configuration"
    )

    st.info(
        "The API key is read only from Streamlit Secrets. "
        "It is not displayed or entered here."
    )

    if get_api_key():

        st.success(
            "🟢 OPENAI_API_KEY detected in Streamlit Secrets."
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

        st.write(response)


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
        "Developed by Engr. Bilal Mehmood"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
