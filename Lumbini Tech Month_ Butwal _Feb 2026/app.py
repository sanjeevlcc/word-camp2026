
import os
import sqlite3
import time
import signal
import socket
from functools import wraps

from flask import Flask, g, request, redirect, url_for, session, render_template, abort
from werkzeug.security import generate_password_hash, check_password_hash

APP_SECRET = os.environ.get("APP_SECRET", "dev-secret-change-me")
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "app.db"))
RUN_MODE = os.environ.get("RUN_MODE", "Traditional (Ubuntu)")
HOSTNAME = socket.gethostname()

app = Flask(__name__)
app.secret_key = APP_SECRET


# ---------------- DB helpers ----------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin','user')),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)
    db.commit()


def seed_admin():
    db = get_db()
    admin = db.execute("SELECT id FROM users WHERE role='admin' LIMIT 1").fetchone()
    if not admin:
        db.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
            ("admin", generate_password_hash("Admin@123"), "admin")
        )
        db.commit()


# ---------------- Auth decorators ----------------
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            abort(403)
        return fn(*args, **kwargs)
    return wrapper


@app.before_request
def _setup():
    init_db()
    seed_admin()


# ---------------- Pages ----------------
@app.get("/")
def home():
    return redirect(url_for("chat") if "user_id" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if not user or not check_password_hash(user["password_hash"], password):
            error = "Invalid username or password."
        else:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("chat"))

    return render_template(
        "index.html",
        view="login",
        title="Login • University Portal",
        error=error,
        run_mode=RUN_MODE,
        hostname=HOSTNAME,
        msgs=[],
        users=[]
    )


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    error = None
    db = get_db()

    if request.method == "POST":
        content = (request.form.get("content") or "").strip()
        if not content:
            error = "Post cannot be empty."
        else:
            db.execute("INSERT INTO messages (user_id, content) VALUES (?,?)", (session["user_id"], content))
            db.commit()
            return redirect(url_for("chat"))

    msgs = db.execute("""
        SELECT m.id, m.content, m.created_at, u.username
        FROM messages m JOIN users u ON u.id=m.user_id
        ORDER BY m.id DESC LIMIT 30
    """).fetchall()

    return render_template(
        "index.html",
        view="chat",
        title="Portal • University Posts",
        error=error,
        run_mode=RUN_MODE,
        hostname=HOSTNAME,
        msgs=msgs,
        users=[]
    )


@app.route("/admin/users", methods=["GET", "POST"])
@admin_required
def admin_users():
    error = None
    db = get_db()

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        role = request.form.get("role") or "user"

        if not username or not password or role not in ("admin", "user"):
            error = "All fields are required and role must be admin/user."
        else:
            try:
                db.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
                    (username, generate_password_hash(password), role)
                )
                db.commit()
                return redirect(url_for("admin_users"))
            except sqlite3.IntegrityError:
                error = "Username already exists. Try another."

    users = db.execute("SELECT id, username, role, created_at FROM users ORDER BY id DESC").fetchall()

    return render_template(
        "index.html",
        view="admin",
        title="Admin • University Portal",
        error=error,
        run_mode=RUN_MODE,
        hostname=HOSTNAME,
        msgs=[],
        users=users
    )


@app.get("/admin/messages/delete/<int:msg_id>")
@admin_required
def delete_message(msg_id: int):
    db = get_db()
    db.execute("DELETE FROM messages WHERE id=?", (msg_id,))
    db.commit()
    return redirect(url_for("chat"))


# ---------------- Demo endpoints (for crash/scaling story) ----------------
@app.get("/healthz")
def healthz():
    return "ok\n", 200


@app.get("/whoami")
def whoami():
    # Helpful when scaling: shows which pod served the request
    return f"mode={RUN_MODE} host={HOSTNAME}\n", 200


@app.get("/crash")
def crash():
    """
    For demo: kill the whole process so service goes DOWN.
    - In Gunicorn: worker receives request, so we also terminate its parent (master).
    - In Docker/K8s: master is PID 1 => container/pod restarts.
    """
    try:
        os.kill(os.getppid(), signal.SIGTERM)
    except Exception:
        pass
    os._exit(1)


@app.get("/burn")
def burn_cpu():
    # CPU burn ~10 seconds (for HPA scaling demo)
    end = time.time() + 10
    x = 0
    while time.time() < end:
        x = (x * 3 + 7) % 9999991
    return f"CPU burn complete: {x}\n"


@app.get("/oom")
def burn_memory():
    # Memory burn (use carefully). In K8s with memory limits, this will trigger OOMKilled + restart.
    data = []
    while True:
        data.append("X" * 10_000_000)  # ~10MB chunks
        time.sleep(0.1)

