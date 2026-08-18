from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "torneio.db"

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
        conn.commit()

# Inicializa o banco de dados SQLite
init_db()

@app.route("/")
def index():
    return render_template("index.html")

# Endpoint para salvar o placar assim que o usuário digita
@app.route("/api/salvar-placar", methods=["POST"])
def salvar_placar():
    data = request.get_json() or {}
    match_id = data.get("match_id")
    score1 = data.get("score1")
    score2 = data.get("score2")

    if not match_id:
        return jsonify({"status": "erro", "mensagem": "match_id obrigatorio"}), 400

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