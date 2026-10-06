# 🇵🇰 PADHO PAKISTAN

## AI-Powered 50-Agent Learning Management System

**Main AI Agent:** Mohammad Ahmad
**Technology:** Python + Streamlit + SQLite + OpenAI API
**Developer:** Engr. Bilal Mehmood

---

## 📚 Overview

**PADHO PAKISTAN** is an AI-powered Learning Management System designed to provide a complete digital learning environment for:

* 👨‍🎓 Students
* 👨‍🏫 Teachers
* 👨‍💼 Administrators
* 🏫 Educational Institutions
* 📚 Departments
* 📖 Courses and Subjects

The system is controlled by a central AI orchestrator named:

# 🤖 Mohammad Ahmad

Mohammad Ahmad acts as the **Main AI Agent** and coordinates **50 specialized AI agents**.

The architecture is:

```text
                 🇵🇰 PADHO PAKISTAN
                         │
                         ▼
              🤖 MOHAMMAD AHMAD
                 MAIN AI AGENT
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     Student Agents  Teacher Agents  Admin Agents
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                  SQLite Database
                         │
                         ▼
                  LMS Information
```

---

# ✨ Key Features

## 👨‍🎓 Student Management

Students can:

* Login
* View profile
* View courses
* View assignments
* Submit assignments
* Attempt quizzes
* View quiz results
* Check attendance
* View academic results
* Access study material
* Use AI Tutor
* Receive notifications
* Follow personalized study plans
* Access achievements

---

## 👨‍🏫 Teacher Management

Teachers can:

* Manage courses
* Create assignments
* Manage quizzes
* Manage attendance
* View students
* Generate lesson plans
* Generate learning content
* View reports
* Use AI Teacher Assistant
* Monitor student performance

---

## 👨‍💼 Administration

Administrators can:

* Manage users
* Manage teachers
* Manage students
* Manage courses
* View assignments
* View results
* Monitor agents
* View agent activity logs
* Check database
* Manage system settings

---

# 🤖 50 AI Agents

PADHO PAKISTAN contains 50 specialized agents controlled by Mohammad Ahmad.

## Academic Agents

1. Student Management Agent
2. Teacher Management Agent
3. Course Management Agent
4. Subject Management Agent
5. Class Management Agent
6. Enrollment Agent
7. Assignment Agent
8. Assignment Submission Agent
9. Assignment Grading Agent
10. Quiz Agent
11. Quiz Evaluation Agent
12. Exam Management Agent
13. Question Bank Agent
14. AI Question Generator Agent
15. Attendance Agent
16. Timetable Agent
17. Study Material Agent
18. AI Tutor Agent
19. AI Lesson Planner Agent
20. Curriculum Agent

## Student Agents

21. Student Performance Agent
22. Personalized Learning Agent
23. Study Planner Agent
24. Reminder Agent
25. Notification Agent
26. Certificate Agent
27. Achievement Agent
28. Career Guidance Agent
29. Coding Practice Agent
30. Project/FYP Agent

## Teacher & AI Agents

31. Teacher Assistant Agent
32. AI Content Generator Agent
33. Rubric Agent
34. Feedback Agent
35. Analytics Agent
36. Dashboard Agent
37. Report Generator Agent
38. PDF Generator Agent
39. Word Document Agent
40. Excel Agent

## Communication & System Agents

41. Announcement Agent
42. Email Agent
43. Discussion Agent
44. Chatbot Agent
45. Search Agent
46. File Management Agent
47. Authentication Agent
48. Security Agent
49. Database Agent
50. System Administration Agent

---

# 🧠 Mohammad Ahmad — Main AI Agent

Mohammad Ahmad is the central intelligence layer.

A user can simply write:

```text
Show my pending assignments
```

Mohammad Ahmad identifies the intent:

```text
User Request
     ↓
Mohammad Ahmad
     ↓
Assignment Agent
     ↓
Database
     ↓
Assignments
```

Another example:

```text
Create a Python quiz
```

The system routes the request:

```text
Mohammad Ahmad
      ↓
Quiz Agent
      ↓
AI Question Generator Agent
      ↓
Quiz
```

---

# 📝 Assignment System

Teachers can create:

* Assignment title
* Course
* Instructions
* Due date
* Total marks
* Teacher information

Students can:

* View assignments
* Read instructions
* Upload files
* Enter text submissions
* Submit assignments
* Track submission status

Supported files include:

```text
PDF
DOCX
DOC
TXT
PY
CSV
XLSX
PPTX
```

---

# 🧠 Quiz System

The LMS provides an interactive quiz system.

Teachers can create:

* Quiz title
* Course
* Questions
* Multiple-choice options
* Correct answer
* Duration

Students can:

* Start quiz
* Select answers
* Submit quiz
* Receive score
* View percentage

Example:

```text
Question:
Which language is widely used for AI?

A. HTML
B. Python
C. CSS
D. SQL

Correct Answer:
Python
```

---

# 📋 Attendance System

Teachers can record:

* Present
* Absent
* Late
* Leave

The system calculates attendance percentage.

Example:

```text
Present = 18
Total = 20

Attendance = 90%
```

---

# 📊 Results

The system supports:

* Marks
* Grades
* Grade points
* Semester
* Student results
* Performance records

The architecture can be extended to support:

* GPA
* CGPA
* Transcript generation
* Semester results
* Course-wise performance

---

# 🤖 AI Tutor

Students can ask:

```text
Explain Python loops
```

The AI Tutor can provide:

1. Concept explanation
2. Examples
3. Practical examples
4. Short quiz
5. Key points

The AI Tutor operates under Mohammad Ahmad.

---

# 🧑‍🏫 AI Lesson Planner

Teachers can enter:

```text
Python Functions
```

The AI Lesson Planner can generate:

* Learning objectives
* Introduction
* Teaching activities
* Examples
* Student activities
* Assessment
* Homework
* Learning outcomes

---

# 🔐 Authentication

PADHO PAKISTAN uses role-based authentication.

Supported roles:

```text
Admin
Teacher
Student
```

Additional roles can be added later:

```text
Principal
HOD
Parent/Guardian
Super Admin
```

Passwords are stored using SHA-256 hashing in the current implementation.

---

# 🗄️ Database

The application uses:

```text
SQLite
```

Database location:

```text
data/padho_pakistan.db
```

The database is automatically created when the application starts.

Main database tables include:

```text
users
courses
assignments
submissions
quizzes
quiz_attempts
attendance
results
materials
notifications
announcements
agent_logs
settings
```

---

# 📁 Project Structure

Recommended project structure:

```text
padho_pakistan/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   └── padho_pakistan.db
│
├── uploads/
│
└── .streamlit/
    └── secrets.toml
```

The current application is designed as a single Streamlit application for easy deployment.

It can later be modularized into:

```text
agents/
pages/
services/
database/
utils/
```

---

# 🔑 OpenAI API Configuration

The API key is **not stored inside `app.py`**.

PADHO PAKISTAN reads the API key from Streamlit Secrets.

Create:

```text
.streamlit/secrets.toml
```

Add:

```toml
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
OPENAI_MODEL = "gpt-5.6"
AI_MODE = "API"
```

Replace:

```text
YOUR_OPENAI_API_KEY
```

with your actual API key.

---

# 🧪 Demo Mode

PADHO PAKISTAN can also run without an API key.

Change:

```toml
AI_MODE = "API"
```

to:

```toml
AI_MODE = "DEMO"
```

Demo Mode provides simulated AI responses so the LMS can be tested without consuming API credits.

---

# ⚙️ Installation

## 1. Install Python

Install Python 3.10 or newer.

Verify:

```bash
python --version
```

or:

```bash
py --version
```

---

# 2. Create Project Folder

```bash
mkdir padho_pakistan
cd padho_pakistan
```

---

# 3. Create Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# 4. Install Requirements

```bash
pip install -r requirements.txt
```

Required packages:

```text
streamlit
openai
pandas
reportlab
python-docx
openpyxl
```

---

# 5. Run Application

```bash
streamlit run app.py
```

The application will open in the browser.

Usually:

```text
http://localhost:8501
```

---

# 🔐 Demo Login Accounts

## Administrator

```text
Username: admin
Password: admin123
```

## Teacher

```text
Username: teacher
Password: teacher123
```

## Student

```text
Username: student
Password: student123
```

These credentials are for demonstration/testing purposes.

Change them before deploying the system for real institutional use.

---

# 🧭 Navigation

## Student

```text
Dashboard
Mohammad Ahmad
Assignments
Submit Assignment
Quizzes
Attendance
Results
Study Materials
Notifications
AI Tutor
All 50 Agents
Settings
Logout
```

## Teacher

```text
Dashboard
Mohammad Ahmad
Assignments
Submit Assignment
Quizzes
Attendance
Results
Study Materials
AI Tutor
Manage Assignments
Manage Quizzes
Manage Attendance
Students
Course Management
AI Lesson Planner
Reports
All 50 Agents
Settings
Logout
```

## Administrator

```text
Dashboard
Mohammad Ahmad
Users
Courses
All Assignments
All Results
Agent Management
Agent Logs
System Settings
Database
All 50 Agents
Settings
Logout
```

---

# 🔄 AI Agent Workflow

The basic workflow is:

```text
USER
 │
 ▼
MOHAMMAD AHMAD
 │
 ▼
INTENT DETECTION
 │
 ▼
AGENT ROUTING
 │
 ▼
SPECIALIZED AGENT
 │
 ▼
DATABASE / AI / FILE
 │
 ▼
VALIDATION
 │
 ▼
RESULT
 │
 ▼
USER
```

---

# 📜 Agent Activity Logs

PADHO PAKISTAN records agent activity.

Each request can record:

```text
Username
Role
Request
Selected Agent
Status
Timestamp
```

Example:

```text
Student
student
"Show my assignments"
Assignment Agent
Success
2026-10-06
```

This provides visibility into how Mohammad Ahmad is routing tasks.

---

# 📄 Reports

The system can generate data reports for:

* Assignments
* Quiz results
* Attendance
* Student performance

Reports can be exported as CSV.

Future versions can add:

* PDF reports
* DOCX reports
* Excel reports
* Student transcripts
* Teacher performance reports
* Department reports

---

# 📦 File Uploads

Uploaded files are stored in:

```text
uploads/
```

The system can support educational files such as:

```text
PDF
DOCX
PPTX
XLSX
CSV
TXT
PY
```

---

# 🇵🇰 Educational Use

PADHO PAKISTAN can be adapted for:

* Universities
* Colleges
* Schools
* Technical institutes
* Vocational institutes
* Training centers
* Engineering departments
* Computer science departments
* AI training centers

It can support academic structures such as:

```text
Institution
    ↓
Department
    ↓
Program
    ↓
Batch
    ↓
Semester
    ↓
Course
    ↓
Students
```

---

# 🚀 Future Development

The platform is designed for further expansion.

Planned features can include:

### 👨‍👩‍👧 Parent Portal

Parents can view:

* Attendance
* Results
* Assignments
* Notifications
* Student performance

### 🎙️ Voice AI

Add voice interaction:

```text
Student
   ↓
Voice
   ↓
Mohammad Ahmad
   ↓
Agent
   ↓
Voice Response
```

### 📱 Mobile Application

Future mobile clients can communicate with the LMS backend through APIs.

### 📚 RAG-Based Learning

Course PDFs and notes can be indexed so students can ask:

```text
According to my course notes,
explain supervised learning.
```

### 🧠 Personalized AI

Mohammad Ahmad can analyze:

```text
Attendance
+
Quiz Results
+
Assignments
+
Exam Results
+
Learning History
```

and produce a personalized learning plan.

---

# 🏆 Long-Term Vision

PADHO PAKISTAN is intended to become a complete:

## 🇵🇰 AI Digital Education Ecosystem

with:

```text
Students
     │
Teachers
     │
Parents
     │
Administrators
     │
     ▼
MOHAMMAD AHMAD
     │
     ▼
50 AI AGENTS
     │
     ▼
INTELLIGENT LMS
```

---

# 🛡️ Security Notes

For production deployment:

* Use stronger password hashing such as Argon2/bcrypt.
* Enable HTTPS.
* Use secure session management.
* Restrict uploaded file types.
* Add file-size limits.
* Validate uploaded files.
* Never commit `secrets.toml` to GitHub.
* Never hard-code OpenAI API keys.
* Use environment-specific secrets.
* Implement database backups.
* Add administrator audit logs.
* Add proper CSRF/session protections where applicable.

---

# 🚫 GitHub Security

Do **NOT** upload:

```text
.streamlit/secrets.toml
```

to GitHub.

Add this to `.gitignore`:

```gitignore
.streamlit/secrets.toml
venv/
__pycache__/
*.pyc
data/*.db
uploads/
```

---

# 🌐 Streamlit Deployment

For Streamlit Cloud:

1. Upload the project to GitHub.
2. Open your Streamlit deployment dashboard.
3. Select the repository.
4. Select:

```text
app.py
```

5. Add your API key under Streamlit Secrets.

Use:

```toml
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
OPENAI_MODEL = "gpt-5.6"
AI_MODE = "API"
```

Do not place the API key in the GitHub source code.

---

# 🧪 Testing

Before deployment, test:

```text
✓ Login
✓ Logout
✓ Student dashboard
✓ Teacher dashboard
✓ Admin dashboard
✓ Assignment creation
✓ Assignment submission
✓ Quiz creation
✓ Quiz attempt
✓ Attendance
✓ Results
✓ AI Tutor
✓ AI Lesson Planner
✓ Mohammad Ahmad
✓ Agent routing
✓ 50-agent navigation
✓ Agent logs
✓ Database
✓ API configuration
✓ Demo Mode
```

---

# 📌 Example AI Commands

Students can ask Mohammad Ahmad:

```text
Show my assignments.
```

```text
What is my attendance?
```

```text
Teach me Python functions.
```

```text
Create a study plan for my exam.
```

```text
Explain machine learning.
```

Teachers can ask:

```text
Create an assignment on Python loops.
```

```text
Generate a quiz about artificial intelligence.
```

```text
Create a lesson plan for data science.
```

```text
Show student performance.
```

Administrators can ask:

```text
Show all courses.
```

```text
Show agent activity.
```

```text
Show system statistics.
```

---

# 👨‍💻 Developer

**Engr. Bilal Mehmood**

AI Course Director / AI Instructor
PITAC Regional Center Karachi, Sindh

---

# 🇵🇰 PADHO PAKISTAN

### Learn. Practice. Perform. Succeed.

**Main AI Agent:** Mohammad Ahmad

**50 Specialized AI Agents**

**AI-Powered Learning Management System**

---
