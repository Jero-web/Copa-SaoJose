from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import sqlite3
import os
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "troque-esta-chave-em-producao")
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "torneio.db")
BRASILIA_TZ = ZoneInfo("America/Sao_Paulo")

MATCH_TEAMS = {
    "m-qf1": ("E.C. Clube Santos Dumont", "Fut Resenha F.C."),
    "m-qf2": ("Veterano do Suti", "Acessórios Modernos"),
    "m-qf3": ("DR Fardamentos", "Boca Junior"),
    "m-qf4": ("Bruxos F.C.", "HMC"),
    "m-sf1": ("Semifinal 1", "Semifinal 1"),
    "m-sf2": ("Semifinal 2", "Semifinal 2"),
    "m-final": ("Finalista 1", "Finalista 2"),
    "feminino-f1": ("ECCF Cancelão", "Ella's Esporte Clube"),
    "feminino-f2": ("Real Meninas", "Envolventes"),
    "feminino-f3": ("Ella's Esporte Clube", "Envolventes"),
    "feminino-f4": ("Real Meninas", "ECCF Cancelão"),
    "feminino-f5": ("ECCF Cancelão", "Envolventes"),
    "feminino-f6": ("Real Meninas", "Ella's Esporte Clube"),
    "s12-qf1": ("Colégio Irmã Mariele", "Reis da Bola"),
    "s12-qf2": ("Meninos de Ouro", "Projeto Coração Valente"),
    "s12-qf3": ("IBV FUT7", "Fortaleza"),
    "s12-qf4": ("Escolinha Paulista", "Netus Tobias"),
    "s12-sf1": ("Semifinal 1", "Semifinal 1"),
    "s12-sf2": ("Semifinal 2", "Semifinal 2"),
    "s12-final": ("Finalista 1", "Finalista 2"),
    "s12-third": ("Perdedor SF 1", "Perdedor SF 2"),
}

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS partidas (
                match_id TEXT PRIMARY KEY,
                score1 INTEGER,
                score2 INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                nome_usuario TEXT NOT NULL,
                acao TEXT NOT NULL,
                data_hora TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        cursor.execute("""
            DELETE FROM logs
            WHERE id NOT IN (
                SELECT id
                FROM logs
                ORDER BY datetime(data_hora) DESC, id DESC
                LIMIT 20
            )
        """)
        if cursor.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
            default_name = os.environ.get("ADMIN_NAME", "admin")
            default_password = os.environ.get("ADMIN_PASSWORD", "123456")
            cursor.execute(
                "INSERT INTO usuarios (nome, senha) VALUES (?, ?)",
                (default_name, generate_password_hash(default_password))
            )
        conn.commit()


def current_user():
    user_id = session.get("usuario_id")
    if not user_id:
        return None
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute("SELECT id, nome FROM usuarios WHERE id = ?", (user_id,)).fetchone()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            if request.path.startswith("/api/"):
                return jsonify({"status": "erro", "mensagem": "Autenticacao necessaria"}), 401
            flash("Faça login para continuar.", "erro")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def add_log(acao):
    user = current_user()
    if not user:
        return
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO logs (usuario_id, nome_usuario, acao, data_hora) VALUES (?, ?, ?, ?)",
            (user["id"], user["nome"], acao, datetime.now(BRASILIA_TZ).isoformat(timespec="seconds"))
        )
        conn.execute("""
            DELETE FROM logs
            WHERE id NOT IN (
                SELECT id
                FROM logs
                ORDER BY datetime(data_hora) DESC, id DESC
                LIMIT 20
            )
        """)
        conn.commit()


@app.template_filter("data_brasilia")
def format_log_datetime(value):
    if not value:
        return ""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(BRASILIA_TZ).strftime("%d/%m/%Y às %H:%M:%S")
    except (TypeError, ValueError):
        return value

# Inicializa o banco de dados SQLite
init_db()

@app.route("/")
def index():
    user = current_user()
    return render_template("index.html", usuario=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        senha = request.form.get("senha", "")
        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = sqlite3.Row
            user = conn.execute("SELECT * FROM usuarios WHERE nome = ?", (nome,)).fetchone()
        if user and check_password_hash(user["senha"], senha):
            session.clear()
            session["usuario_id"] = user["id"]
            add_log("Login efetuado")
            return redirect(url_for("index", category="masculino"))
        flash("Nome ou senha inválidos.", "erro")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    add_log("Logout efetuado")
    session.clear()
    return redirect(url_for("index"))


@app.route("/cadastrar", methods=["GET", "POST"])
@login_required
def cadastrar():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        senha = request.form.get("senha", "")
        if not nome:
            flash("Informe o nome do usuário.", "erro")
        elif not re.fullmatch(r"[0-9]{6}", senha):
            flash("A senha deve conter exatamente 6 dígitos numéricos.", "erro")
        else:
            try:
                with sqlite3.connect(DB_NAME) as conn:
                    conn.execute("INSERT INTO usuarios (nome, senha) VALUES (?, ?)", (nome, generate_password_hash(senha)))
                    conn.commit()
                add_log(f"Usuário cadastrado: {nome}")
                flash("Usuário cadastrado com sucesso.", "sucesso")
                return redirect(url_for("cadastrar"))
            except sqlite3.IntegrityError:
                flash("Esse nome de usuário já está cadastrado.", "erro")
    return render_template("cadastrar.html", usuario=current_user())


@app.route("/logs")
@login_required
def logs():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        registros = conn.execute("""
            SELECT nome_usuario, data_hora, acao
            FROM logs
            ORDER BY datetime(data_hora) DESC, id DESC
            LIMIT 20
        """).fetchall()
    return render_template("logs.html", usuario=current_user(), logs=registros)

# Endpoint para salvar o placar assim que o usuário digita
@app.route("/api/salvar-placar", methods=["POST"])
def salvar_placar():
    user = current_user()
    if not user:
        return jsonify({"status": "erro", "mensagem": "Autenticacao necessaria"}), 401
    data = request.get_json() or {}
    match_id = data.get("match_id")
    score1 = data.get("score1")
    score2 = data.get("score2")

    if not match_id or match_id not in MATCH_TEAMS:
        return jsonify({"status": "erro", "mensagem": "match_id obrigatorio"}), 400
    if any(value is not None and (not isinstance(value, int) or value < 0) for value in (score1, score2)):
        return jsonify({"status": "erro", "mensagem": "Placar invalido"}), 400

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO partidas (match_id, score1, score2)
            VALUES (?, ?, ?)
            ON CONFLICT(match_id) DO UPDATE SET
                score1 = excluded.score1,
                score2 = excluded.score2
        """, (match_id, score1, score2))
        conn.commit()

    team1, team2 = MATCH_TEAMS[match_id]
    add_log(f"Alteração de placar: {team1} {score1 if score1 is not None else '-'} x {score2 if score2 is not None else '-'} {team2}")

    return jsonify({"status": "sucesso"})

# Endpoint para carregar os placares salvos ao abrir o navegador
@app.route("/api/obter-placares", methods=["GET"])
def obter_placares():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT match_id, score1, score2 FROM partidas")
        rows = cursor.fetchall()
    
    placares = {row[0]: {"score1": row[1], "score2": row[2]} for row in rows}
    return jsonify(placares)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)