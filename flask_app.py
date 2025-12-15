from flask import Flask, redirect, render_template, request, url_for
from dotenv import load_dotenv
import os
import git
import hmac
import hashlib
from db import db_read, db_write
from auth import login_manager, authenticate, register_user
from flask_login import login_user, logout_user, login_required, current_user
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Load .env variables
load_dotenv()
W_SECRET = os.getenv("W_SECRET")

# Init flask app
app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "supersecret"

# Init auth
login_manager.init_app(app)
login_manager.login_view = "login"

# DON'T CHANGE
def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)

# DON'T CHANGE
@app.post('/update_server')
def webhook():
    x_hub_signature = request.headers.get('X-Hub-Signature')
    if is_valid_signature(x_hub_signature, request.data, W_SECRET):
        repo = git.Repo('./mysite')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    return 'Unathorized', 401

# Auth routes
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        user = authenticate(
            request.form["username"],
            request.form["password"]
        )

        if user:
            login_user(user)
            return redirect(url_for("index"))

        error = "Benutzername oder Passwort ist falsch."

    return render_template(
        "auth.html",
        title="In dein Konto einloggen",
        action=url_for("login"),
        button_label="Einloggen",
        error=error,
        footer_text="Noch kein Konto?",
        footer_link_url=url_for("register"),
        footer_link_label="Registrieren"
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        ok = register_user(username, password)
        if ok:
            return redirect(url_for("login"))

        error = "Benutzername existiert bereits."

    return render_template(
        "auth.html",
        title="Neues Konto erstellen",
        action=url_for("register"),
        button_label="Registrieren",
        error=error,
        footer_text="Du hast bereits ein Konto?",
        footer_link_url=url_for("login"),
        footer_link_label="Einloggen"
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))



# App routes
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # GET
    if request.method == "GET":
        todos = db_read("SELECT id, content, due FROM todos WHERE user_id=%s ORDER BY due", (current_user.id,))
        return render_template("main_page.html", todos=todos)

    # POST
    content = request.form["contents"]
    due = request.form["due_at"]
    db_write("INSERT INTO todos (user_id, content, due) VALUES (%s, %s, %s)", (current_user.id, content, due, ))
    return redirect(url_for("index"))

@app.post("/complete")
@login_required
def complete():
    todo_id = request.form.get("id")
    db_write("DELETE FROM todos WHERE user_id=%s AND id=%s", (current_user.id, todo_id,))
    return redirect(url_for("index"))

@app.route("/dbexplorer", methods=["GET", "POST"])
@login_required
def dbexplorer():
    # Alle Tabellennamen holen
    tables_raw = db_read("SHOW TABLES")
    all_tables = [next(iter(row.values())) for row in tables_raw]  # erste Spalte jedes Dicts

    selected_tables = []
    limit = 50  # Default
    results = {}

    if request.method == "POST":
        # Gewählte Tabellen einsammeln
        selected_tables = request.form.getlist("tables")

        # Limit aus Formular lesen
        limit_str = request.form.get("limit") or ""
        try:
            limit = int(limit_str)
        except ValueError:
            limit = 50

        # Limit ein bisschen absichern
        if limit < 1:
            limit = 1
        elif limit > 1000:
            limit = 1000

        allowed = set(all_tables)

        # Pro gewählter Tabelle Daten abfragen
        for table in selected_tables:
            if table in allowed:  # einfache Absicherung gegen SQL-Injection
                rows = db_read(f"SELECT * FROM `{table}` LIMIT %s", (limit,))
                results[table] = rows

    return render_template(
        "dbexplorer.html",
        all_tables=all_tables,
        selected_tables=selected_tables,
        results=results,
        limit=limit,
    )

from flask import render_template
from flask_login import login_required

# Use the same DB helper you already use elsewhere in your app:
# (If your project names it differently, replace db_read accordingly.)
from db import db_read


@app.route("/db-visualization", methods=["GET"])
@login_required  # remove this line if you want it public
def db_visualization():
    users = db_read("SELECT id, username FROM users ORDER BY id")
    todos = db_read("SELECT id, user_id, content, due FROM todos ORDER BY user_id, id")

    # group todos by user_id
    todos_by_user = {}
    for t in todos:
        todos_by_user.setdefault(t["user_id"], []).append(t)

    # Hierarchical Edge Bundling expects:
    # [{ name: "a.b.c", imports: ["x.y.z", ...] }, ...]
    graph_data = []

    # todo leaves
    for t in todos:
        tid = t["id"]
        graph_data.append({
            "name": f"db.todos.todo_{tid}",
            "label": t["content"],
            "type": "todo",
            "imports": []
        })

    # user leaves + edges to their todos
    for u in users:
        uid = u["id"]
        uname = u["username"]
        graph_data.append({
            "name": f"db.users.user_{uid}",
            "label": uname,
            "type": "user",
            "imports": [f"db.todos.todo_{t['id']}" for t in todos_by_user.get(uid, [])]
        })

    return render_template("db_visualization.html", graph_data=graph_data)




if __name__ == "__main__":
    app.run()
