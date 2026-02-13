# app.py
# University Portal (Demo CRUD App)
# Features:
# - Login (admin/user) with password hashing
# - CRUD messages (student posts) [Create + Read + Delete (admin)]
# - Admin can create users + delete messages
# - Demo endpoints: /crash, /burn, /oom, /healthz
#
# Default Admin:
#   username: admin
#   password: Admin@123




import os
import sqlite3
import time
from functools import wraps

from flask import (
    Flask, g, request, redirect, url_for, session,
    render_template_string, abort
)
from werkzeug.security import generate_password_hash, check_password_hash

APP_SECRET = os.environ.get("APP_SECRET", "dev-secret-change-me")
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "app.db"))

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
    admin = db.execute("SELECT * FROM users WHERE role='admin' LIMIT 1").fetchone()
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






# ---------------- UI (Modern, colorful) ----------------
BASE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{{ title }}</title>
  <style>
    :root{
      --bg1:#0b1220; --bg2:#0a0f1a;
      --border: rgba(255,255,255,.12);
      --text: rgba(255,255,255,.92);
      --muted: rgba(255,255,255,.68);
      --shadow: 0 18px 60px rgba(0,0,0,.45);
      --grad: linear-gradient(135deg,#7c3aed 0%,#22c55e 45%,#06b6d4 100%);
      --grad2: linear-gradient(135deg,#f97316 0%,#ec4899 50%,#8b5cf6 100%);
      --danger:#fb7185; --ok:#34d399;
      --btn: rgba(255,255,255,.10);
      --btnH: rgba(255,255,255,.16);
      --ring: 0 0 0 3px rgba(34,197,94,.20);
      --radius: 18px;
    }
    *{box-sizing:border-box}
    body{
      margin:0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
      color: var(--text);
      background:
        radial-gradient(900px 500px at 15% 10%, rgba(124,58,237,.35), transparent 60%),
        radial-gradient(900px 600px at 85% 20%, rgba(6,182,212,.22), transparent 55%),
        radial-gradient(900px 600px at 30% 90%, rgba(34,197,94,.20), transparent 55%),
        linear-gradient(180deg, var(--bg1), var(--bg2));
      min-height:100vh;
    }
    a{color:inherit; text-decoration:none}
    .wrap{max-width:1020px; margin:0 auto; padding:22px 16px 40px}
    .nav{
      display:flex; align-items:center; justify-content:space-between;
      padding:14px 16px; border:1px solid var(--border);
      background: rgba(255,255,255,.04);
      border-radius: var(--radius);
      backdrop-filter: blur(14px);
      box-shadow: var(--shadow);
      position: sticky; top: 12px; z-index: 10;
    }
    .brand{display:flex; gap:12px; align-items:center}
    .logo{
      width:44px; height:44px; border-radius:14px;
      background: var(--grad);
      box-shadow: 0 10px 30px rgba(124,58,237,.25);
      display:grid; place-items:center;
      font-weight:900;
    }
    .brand h1{font-size:16px; margin:0}
    .brand .sub{font-size:12px; color:var(--muted)}
    .right{display:flex; gap:10px; align-items:center; flex-wrap:wrap; justify-content:flex-end}
    .pill{
      border:1px solid var(--border);
      background: rgba(255,255,255,.05);
      padding:7px 10px;
      border-radius: 999px;
      font-size:12px;
      color: var(--muted);
      display:flex; gap:8px; align-items:center;
    }
    .dot{width:8px;height:8px;border-radius:99px;background:var(--ok)}
    .btn{
      border:1px solid var(--border);
      background: var(--btn);
      padding:9px 12px;
      border-radius: 12px;
      transition:.2s;
      cursor:pointer;
      font-weight:600;
      display:inline-flex;
      align-items:center;
      gap:10px;
    }
    .btn:hover{background:var(--btnH); transform: translateY(-1px)}
    .btn.primary{
      border:none;
      background: var(--grad2);
      color:#0b1220;
      box-shadow: 0 14px 40px rgba(236,72,153,.18);
    }
    .grid{
      margin-top:18px;
      display:grid;
      grid-template-columns: 1.25fr .75fr;
      gap: 16px;
      align-items:start;
    }
    @media (max-width: 900px){
      .grid{grid-template-columns: 1fr}
      .nav{position:relative; top:auto}
    }
    .card{
      border:1px solid var(--border);
      background: rgba(255,255,255,.05);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow:hidden;
    }
    .card .hd{
      padding:16px 16px 10px;
      border-bottom:1px solid rgba(255,255,255,.08);
      background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
    }
    .title{margin:0; font-size:18px}
    .muted{color:var(--muted); font-size:13px; line-height:1.45}
    .card .bd{padding:16px}
    .field label{
      display:block;
      color:var(--muted);
      font-size:12px;
      margin-bottom:6px;
    }
    input, textarea, select{
      width:100%;
      padding:12px 12px;
      border-radius: 14px;
      border:1px solid rgba(255,255,255,.12);
      background: rgba(10,15,26,.55);
      color:var(--text);
      outline:none;
      transition:.15s;
    }
    textarea{resize: vertical; min-height: 92px}
    input:focus, textarea:focus, select:focus{box-shadow: var(--ring); border-color: rgba(34,197,94,.40)}
    .actions{display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-top:10px}
    .alert{
      border:1px solid rgba(251,113,133,.25);
      background: rgba(251,113,133,.10);
      padding:10px 12px;
      border-radius: 14px;
      color: rgba(255,255,255,.92);
      margin-top: 12px;
    }
    .badge{
      font-size: 12px;
      padding: 6px 10px;
      border-radius: 999px;
      border:1px solid rgba(255,255,255,.12);
      background: rgba(255,255,255,.06);
      color: var(--muted);
    }
    .feed{display:flex; flex-direction:column; gap:10px;}
    .msg{
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.05);
      border-radius: 16px;
      padding: 12px 12px;
    }
    .msg .meta{
      display:flex; gap:10px; align-items:center; justify-content:space-between;
      margin-bottom: 8px;
    }
    .msg .who{font-weight:800}
    .msg .when{font-size:12px; color: var(--muted)}
    .msg .content{white-space:pre-wrap; line-height:1.45}
    .tools{margin-top:10px; display:flex; gap:10px; align-items:center}
    .link{
      font-size:12px;
      color: rgba(255,255,255,.86);
      border:1px solid rgba(255,255,255,.12);
      background: rgba(255,255,255,.06);
      padding:7px 10px;
      border-radius: 999px;
      display:inline-flex;
      gap:8px;
      align-items:center;
      transition:.2s;
    }
    .link:hover{background: rgba(255,255,255,.10)}
    .kbd{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 11px;
      color: rgba(255,255,255,.78);
      background: rgba(255,255,255,.06);
      border:1px solid rgba(255,255,255,.10);
      padding: 2px 6px;
      border-radius: 8px;
      margin-left: 6px;
    }
    .footer{
      margin-top: 14px;
      color: rgba(255,255,255,.55);
      font-size: 12px;
      text-align:center;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="nav">
      <div class="brand">
        <div class="logo">UP</div>
        <div>
          <h1>University Portal</h1>
          <div class="sub">Traditional → Docker → Kubernetes demo app</div>
        </div>
      </div>

      <div class="right">
        {% if session.get('username') %}
          <div class="pill">
            <span class="dot"></span>
            <span>Signed in as <b style="color:rgba(255,255,255,.92)">{{ session.get('username') }}</b></span>
            <span class="badge">{{ session.get('role') }}</span>
          </div>
          {% if session.get('role') == 'admin' %}
            <a class="btn" href="{{ url_for('admin_users') }}">Admin Panel</a>
          {% endif %}
          <a class="btn primary" href="{{ url_for('logout') }}">Logout</a>
        {% else %}
          <a class="btn primary" href="{{ url_for('login') }}">Login</a>
        {% endif %}
      </div>
    </div>

    {% if error %}
      <div class="alert"><b>Oops:</b> {{ error }}</div>
    {% endif %}

    {{ body|safe }}

    <div class="footer">
      Demo endpoints:
      <span class="kbd">/crash</span> <span class="kbd">/burn</span>
      <span class="kbd">/oom</span> <span class="kbd">/healthz</span>
    </div>
  </div>
</body>
</html>
"""

LOGIN_PAGE = """
<div class="grid">
  <div class="card">
    <div class="hd">
      <p class="muted" style="margin:0">Welcome</p>
      <h2 class="title" style="margin-top:6px">Sign in</h2>
      <p class="muted" style="margin-top:8px">
        Admin creates users. Default admin shown below.
      </p>
    </div>
    <div class="bd">
      <form method="post">
        <div class="field">
          <label>Username</label>
          <input name="username" placeholder="e.g., student1, admin" required />
        </div>
        <div class="field">
          <label>Password</label>
          <input name="password" type="password" placeholder="••••••••" required />
        </div>
        <div class="actions">
          <button class="btn primary" type="submit">Login</button>
          <span class="muted">Role-based portal demo</span>
        </div>
      </form>

      <div class="alert" style="border-color:rgba(52,211,153,.25); background: rgba(52,211,153,.10); margin-top:14px">
        <b>Default Admin:</b> admin / Admin@123
        <span class="muted">(change after demo)</span>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="hd">
      <h3 class="title" style="margin:0">Demo Actions</h3>
      <p class="muted" style="margin-top:6px">Use these endpoints during the talk.</p>
    </div>
    <div class="bd">
      <div class="feed">
        <div class="msg">
          <div class="meta"><div class="who">Crash</div><div class="when">instant exit</div></div>
          <div class="content"><a class="link" href="/crash">Open /crash</a></div>
        </div>
        <div class="msg">
          <div class="meta"><div class="who">Load</div><div class="when">CPU burn</div></div>
          <div class="content"><a class="link" href="/burn">Open /burn</a></div>
        </div>
        <div class="msg">
          <div class="meta"><div class="who">OOM</div><div class="when">memory pressure</div></div>
          <div class="content"><a class="link" href="/oom">Open /oom</a></div>
        </div>
        <div class="msg">
          <div class="meta"><div class="who">Health</div><div class="when">probe</div></div>
          <div class="content"><a class="link" href="/healthz">Open /healthz</a></div>
        </div>
      </div>
    </div>
  </div>
</div>
"""

CHAT_PAGE = """
<div class="grid">
  <div class="card">
    <div class="hd">
      <h2 class="title" style="margin:0">University Notice / Student Posts</h2>
      <p class="muted" style="margin-top:6px">
        Students can post updates. Admin can delete posts and create users.
      </p>
    </div>
    <div class="bd">
      <form method="post">
        <div class="field">
          <label>Write a post</label>
          <textarea name="content" placeholder="e.g., Exam schedule, admission notice, help request..." required></textarea>
        </div>
        <div class="actions">
          <button class="btn primary" type="submit">Post</button>
          <a class="link" href="/burn">Simulate Load</a>
          <a class="link" href="/crash">Crash App</a>
          <a class="link" href="/oom">OOM</a>
        </div>
      </form>
    </div>
  </div>

  <div class="card">
    <div class="hd">
      <h3 class="title" style="margin:0">System Status</h3>
      <p class="muted" style="margin-top:6px">Useful for narration.</p>
    </div>
    <div class="bd">
      <div class="feed">
        <div class="msg"><div class="meta"><div class="who">Mode</div><div class="when">{{ mode }}</div></div></div>
        <div class="msg"><div class="meta"><div class="who">Database</div><div class="when">SQLite (local)</div></div></div>
        <div class="msg"><div class="meta"><div class="who">User</div><div class="when">{{ session.get('username') }}</div></div></div>
        <div class="msg"><div class="meta"><div class="who">Role</div><div class="when">{{ session.get('role') }}</div></div></div>
        <div class="muted">K8s demo: <span class="kbd">kubectl get pods -w</span></div>
      </div>
    </div>
  </div>
</div>

<div class="card" style="margin-top:16px">
  <div class="hd">
    <h3 class="title" style="margin:0">Recent Posts</h3>
    <p class="muted" style="margin-top:6px">Latest 30 posts (newest first).</p>
  </div>
  <div class="bd">
    <div class="feed">
      {% for m in msgs %}
        <div class="msg">
          <div class="meta">
            <div><span class="who">{{ m['username'] }}</span> <span class="badge" style="margin-left:8px">user</span></div>
            <div class="when">{{ m['created_at'] }}</div>
          </div>
          <div class="content">{{ m['content']|e }}</div>

          {% if session.get('role') == 'admin' %}
            <div class="tools">
              <a class="link" href="{{ url_for('delete_message', msg_id=m['id']) }}">Delete</a>
              <span class="muted">Admin moderation</span>
            </div>
          {% endif %}
        </div>
      {% endfor %}

      {% if not msgs %}
        <div class="muted">No posts yet. Start by posting the first notice 👋</div>
      {% endif %}
    </div>
  </div>
</div>
"""

ADMIN_USERS_PAGE = """
<div class="grid">
  <div class="card">
    <div class="hd">
      <h2 class="title" style="margin:0">Admin Panel</h2>
      <p class="muted" style="margin-top:6px">
        Create users (role required: admin/user).
      </p>
    </div>
    <div class="bd">
      <form method="post">
        <div class="field">
          <label>Username</label>
          <input name="username" placeholder="e.g., student2" required />
        </div>
        <div class="field">
          <label>Password</label>
          <input name="password" type="password" placeholder="Set a password" required />
        </div>
        <div class="field">
          <label>Role</label>
          <select name="role">
            <option value="user">user</option>
            <option value="admin">admin</option>
          </select>
        </div>
        <div class="actions">
          <button class="btn primary" type="submit">Create User</button>
          <span class="muted">Create 3–5 demo users quickly.</span>
        </div>
      </form>
    </div>
  </div>

  <div class="card">
    <div class="hd">
      <h3 class="title" style="margin:0">Admin Notes</h3>
      <p class="muted" style="margin-top:6px">What to highlight in the talk.</p>
    </div>
    <div class="bd">
      <div class="feed">
        <div class="msg"><div class="meta"><div class="who">Roles</div><div class="when">admin vs user</div></div></div>
        <div class="msg"><div class="meta"><div class="who">Moderation</div><div class="when">delete posts</div></div></div>
        <div class="msg"><div class="meta"><div class="who">Crash</div><div class="when">/crash</div></div></div>
        <div class="msg"><div class="meta"><div class="who">Scale</div><div class="when">/burn + HPA</div></div></div>
      </div>
    </div>
  </div>
</div>

<div class="card" style="margin-top:16px">
  <div class="hd">
    <h3 class="title" style="margin:0">Users</h3>
    <p class="muted" style="margin-top:6px">Newest first.</p>
  </div>
  <div class="bd">
    <div class="feed">
      {% for u in users %}
        <div class="msg">
          <div class="meta">
            <div><span class="who">{{ u['username'] }}</span> <span class="badge" style="margin-left:8px">{{ u['role'] }}</span></div>
            <div class="when">{{ u['created_at'] }}</div>
          </div>
        </div>
      {% endfor %}
    </div>
  </div>
</div>
"""






# ---------------- Routes ----------------
@app.before_request
def _setup():
    init_db()
    seed_admin()


@app.get("/")
def home():
    if "user_id" in session:
        return redirect(url_for("chat"))
    return redirect(url_for("login"))


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

    body = render_template_string(LOGIN_PAGE)
    return render_template_string(BASE, title="Login • University Portal", body=body, error=error)


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    db = get_db()
    error = None

    if request.method == "POST":
        content = (request.form.get("content") or "").strip()
        if not content:
            error = "Post cannot be empty."
        else:
            db.execute(
                "INSERT INTO messages (user_id, content) VALUES (?,?)",
                (session["user_id"], content)
            )
            db.commit()
            return redirect(url_for("chat"))

    msgs = db.execute("""
        SELECT m.id, m.content, m.created_at, u.username
        FROM messages m JOIN users u ON u.id=m.user_id
        ORDER BY m.id DESC LIMIT 30
    """).fetchall()

    mode = os.environ.get("RUN_MODE", "Traditional (Ubuntu)")
    body = render_template_string(CHAT_PAGE, msgs=msgs, mode=mode)
    return render_template_string(BASE, title="Portal • University Posts", body=body, error=error)


@app.route("/admin/users", methods=["GET", "POST"])
@admin_required
def admin_users():
    db = get_db()
    error = None

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
    body = render_template_string(ADMIN_USERS_PAGE, users=users)
    return render_template_string(BASE, title="Admin • University Portal", body=body, error=error)


@app.get("/admin/messages/delete/<int:msg_id>")
@admin_required
def delete_message(msg_id: int):
    db = get_db()
    db.execute("DELETE FROM messages WHERE id=?", (msg_id,))
    db.commit()
    return redirect(url_for("chat"))





# ---------------- Demo endpoints ----------------
@app.get("/healthz")
def healthz():
    return "ok\n", 200


@app.get("/crash")
def crash():
    # kills the process immediately (best for Traditional downtime story with 1 worker)
    os._exit(1)


@app.get("/burn")
def burn_cpu():
    # CPU burn for ~10 seconds (for load/HPA demo)
    end = time.time() + 10
    x = 0
    while time.time() < end:
        x = (x * 3 + 7) % 9999991
    return f"CPU burn complete: {x}\n"


@app.get("/oom")
def burn_memory():
    # Memory burn (use carefully). In K8s with memory limits, this triggers OOMKilled.
    data = []
    while True:
        data.append("X" * 10_000_000)  # ~10MB chunks
        time.sleep(0.1)
