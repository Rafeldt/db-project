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

def build_db_graph(db, schema: str):
    """
    Returns:
      tree  = hierarchical structure: root -> tables -> rows (leaf nodes)
      links = [{source: "tableA:1", target: "tableB:99"}, ...] for cross-table refs
    """
    cur = db.cursor(dictionary=True)

    # 1) list tables
    cur.execute("""
        SELECT TABLE_NAME
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
    """, (schema,))
    tables = [r["TABLE_NAME"] for r in cur.fetchall()]

    # 2) primary key per table (assumes single-column PK; common for school projects)
    pk = {}
    for t in tables:
        cur.execute("""
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_KEY='PRI'
            ORDER BY ORDINAL_POSITION
            LIMIT 1
        """, (schema, t))
        row = cur.fetchone()
        pk[t] = row["COLUMN_NAME"] if row else None

    # 3) foreign keys (cross-table only)
    cur.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA=%s
          AND REFERENCED_TABLE_NAME IS NOT NULL
          AND REFERENCED_TABLE_NAME <> TABLE_NAME
    """, (schema,))
    fks = cur.fetchall()

    # 4) build tree: root -> tables -> leaf rows
    tree = {"name": schema, "children": []}

    for t in tables:
        pkcol = pk.get(t)
        if not pkcol:
            # If a table has no PK, you can skip it or synthesize an id.
            continue

        # IMPORTANT: table/column identifiers can't be parameterized, so we only use values
        # from information_schema (trusted) and quote them with backticks.
        cur.execute(f"SELECT `{pkcol}` AS id FROM `{t}`")
        rows = cur.fetchall()

        tree["children"].append({
            "name": t,
            "children": [
                {
                    "name": str(r["id"]),
                    "id": f"{t}:{r['id']}",      # leaf node id used by D3
                    "table": t,
                    "pk": r["id"],
                }
                for r in rows
            ]
        })

    # 5) build links by reading each FK column values per row
    links = []
    for fk in fks:
        src_table = fk["TABLE_NAME"]
        src_fkcol = fk["COLUMN_NAME"]
        dst_table = fk["REFERENCED_TABLE_NAME"]
        dst_col   = fk["REFERENCED_COLUMN_NAME"]  # usually the PK of dst_table
        src_pkcol = pk.get(src_table)

        if not src_pkcol:
            continue

        cur.execute(
            f"""
            SELECT `{src_pkcol}` AS src_id, `{src_fkcol}` AS ref_val
            FROM `{src_table}`
            WHERE `{src_fkcol}` IS NOT NULL
            """
        )
        for r in cur.fetchall():
            # assumes ref_val matches the referenced column value (typical FK)
            links.append({
                "source": f"{src_table}:{r['src_id']}",
                "target": f"{dst_table}:{r['ref_val']}",
                "from_table": src_table,
                "to_table": dst_table,
                "fk_column": src_fkcol,
            })

    cur.close()
    return tree, links



@app.route("/db-visualization")
def db_visualization_page():
    # render the HTML you already have in templates/db_visualization/...
    # e.g. templates/db_visualization/index.html
    return render_template("db_visualization/index.html")


@app.route("/api/db-visualization")
def db_visualization_data():
    db = get_db()
    schema = db.database  # or your DB name; adjust if your connector differs

    tree, links = build_db_graph(db, schema)
    return jsonify({"tree": tree, "links": links})


if __name__ == "__main__":
    app.run()
