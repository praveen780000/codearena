# CodeArena

A live coding-interview and DSA-practice platform: interviewers create rooms
tied to a question and share a join code; candidates solve it in-browser;
submitted code is actually executed and graded; and submissions are checked
for suspicious similarity to other users' answers on the same question.

> Built by inferring the intended feature set from a partial project (a
> `manage.py` referencing `codearena.settings` and a database with
> `accounts_user`, `interviews_room`, `questions_question`, and
> `submissions_submission` tables — including a `similarity_score` column,
> which is what motivated the plagiarism-style check below). No original
> source files were available, so this is a fresh, complete implementation
> built to match that schema and its evident intent.

## Features

- **Two roles**: interviewers create rooms; students practice and join rooms.
- **Live interview rooms**: an interviewer picks a question, gets a
  6-character room code, and shares it with a candidate.
- **Practice mode**: students can also solve any question independently,
  outside of a room.
- **Real code execution**: submitted Python is actually run against a
  sample input and compared to expected output — not just pattern-matched.
- **Similarity detection**: each submission is compared against every other
  user's submission for the same question; a high match is flagged in the
  UI as a possible copy.

## Architecture

```
┌────────────────────────┐     plain HTTP (REST)     ┌───────────────────────┐
│  Django Web App          │ ─────────────────────────▶ │  FastAPI Judge Service │
│  - Auth (roles: student/  │      POST /judge            │  - runs submitted code │
│    interviewer)            │                              │    via subprocess       │
│  - Rooms, Questions         │ ◀───────────────────────── │  - diffs it against     │
│  - Submissions (MySQL)       │      JSON: output/status/    │    other submissions    │
└────────────────────────┘        similarity_score        └───────────────────────┘
```

- **Django**: auth with a custom `User` model (`role`: student/interviewer),
  room creation/joining, question management, submission history — all via
  the ORM into MySQL (SQLite fallback for local dev).
- **FastAPI**: the actual code execution and similarity-scoring engine —
  intentionally separate from Django because running arbitrary submitted
  code is exactly the kind of workload you don't want inside your main web
  process.

## Tech Stack

| Layer              | Technology                          |
|--------------------|--------------------------------------|
| Web app / auth      | Django 5, session-based auth, custom User model |
| Database            | MySQL (SQLite fallback for local dev) |
| Judge engine         | FastAPI + Python `subprocess`       |
| Similarity check      | `difflib.SequenceMatcher` (textual diff ratio) |
| Service-to-service     | Plain HTTP via `requests` (no auth yet — see below) |

## Project Structure

```
codearena/
├── django_app/
│   ├── manage.py
│   ├── codearena/            # settings, urls, wsgi/asgi
│   ├── accounts/              # custom User model (role field), auth, dashboard
│   ├── questions/              # Question model, practice mode, seed_questions command
│   ├── interviews/              # Room model (auto-generated join codes)
│   └── submissions/              # Submission model + FastAPI client (services.py)
├── fastapi_service/
│   ├── main.py                  # POST /judge endpoint
│   └── judge.py                  # code execution + similarity scoring
└── requirements.txt
```

## Getting Started

### 1. Set up a virtual environment

```bash
git clone https://github.com/<your-username>/codearena.git
cd codearena
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 2. Run the FastAPI judge service

```bash
cd fastapi_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

### 3. Run the Django app (second terminal)

```bash
cd django_app
pip install -r ../requirements.txt
python manage.py migrate
python manage.py seed_questions       # loads 4 sample coding questions
python manage.py createsuperuser      # optional, for /admin
python manage.py runserver
```

Visit `http://127.0.0.1:8000`, register once as an **interviewer** and once
as a **student** (two different accounts/browsers), then:

- As the interviewer: **New Room** → pick a question → share the generated code.
- As the student: **Join Room** → enter the code → write/submit a solution.
- Or skip rooms entirely: as a student, use **Practice** to solve any question directly.

By default Django talks to FastAPI at `http://127.0.0.1:8001`; override with
`FASTAPI_SERVICE_URL` if needed.

### Switching to MySQL

```bash
export USE_MYSQL=True
export DB_NAME=codearena_db
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_HOST=127.0.0.1
export DB_PORT=3306
pip install mysqlclient
```

```sql
CREATE DATABASE codearena_db CHARACTER SET utf8mb4;
```

```bash
python manage.py migrate
```

## How Judging Actually Works

1. Django gathers the submitted code, the question's `sample_input` /
   `sample_output`, and up to 50 other users' code for the same question.
2. It POSTs all of that to FastAPI's `/judge` endpoint.
3. FastAPI writes the code to a temp file and runs it as a subprocess,
   feeding `sample_input` via stdin, with a **5-second timeout**. Exit code
   ≠ 0 → `Error`; stdout matches expected output → `Passed`; otherwise `Failed`.
4. Separately, it diffs the submitted code against every other submission
   for that question using `difflib.SequenceMatcher` and returns the
   highest match plus who it matched.
5. Django saves all of this as a `Submission` row and renders it — with a
   visible warning banner if similarity is ≥80%.

## ⚠️ Known Limitations & Next Steps

Being upfront about this matters more than pretending otherwise:

- **Code execution is NOT securely sandboxed.** The judge runs submitted
  Python directly via `subprocess` with only a timeout as protection. This
  is fine for a local demo or trusted classroom setting, but **must not be
  exposed on the public internet as-is** — it would let anyone run arbitrary
  code on your server. A real deployment needs proper isolation: Docker
  containers with no network access and strict CPU/memory limits, a
  dedicated sandboxing tool (e.g. Judge0, gVisor), or at minimum the `resource`
  module to cap memory/CPU inside the subprocess.
- **Similarity detection is textual, not semantic.** `difflib` catches
  copy-pasted or lightly-edited code, but won't catch someone who
  restructures the same logic (different variable names, reordered lines,
  equivalent loop constructs). A stronger version would normalize code
  first (e.g. via `ast`, similar to the naming/structure analysis approach
  in a related project) before diffing.
- **No auth between Django and FastAPI.** The `/judge` endpoint is open to
  anything that can reach it on the network. Next step: shared API key or
  JWT.
- **No real-time collaboration.** Despite being "interview rooms," this is
  currently request/response — the interviewer doesn't see the candidate's
  code live. A real live-coding feel would need WebSockets (Django Channels)
  to sync the editor between both users.
- **No automated tests yet.**

## License

MIT — feel free to use this as a learning project or portfolio piece. Do
**not** deploy the code-execution feature publicly without addressing the
sandboxing limitation above.
