from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "tarefas.db")


# ===============================
# BANCO
# ===============================

def conectar():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topico_id INTEGER,
            texto TEXT,
            urgencia TEXT,
            concluida INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


criar_banco()


# ===============================
# FRONTEND
# ===============================

@app.route("/")
def index():
    return render_template("index.html")


# ===============================
# API
# ===============================

@app.route("/dados", methods=["GET"])
def carregar_dados():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM topicos")
    topicos_db = cursor.fetchall()

    dados = []

    for topico in topicos_db:
        cursor.execute("""
            SELECT * FROM tarefas
            WHERE topico_id = ?
        """, (topico["id"],))

        tarefas_db = cursor.fetchall()

        tarefas = [{
            "id": t["id"],
            "texto": t["texto"],
            "urgencia": t["urgencia"],
            "concluida": bool(t["concluida"])
        } for t in tarefas_db]

        dados.append({
            "id": topico["id"],
            "nome": topico["nome"],
            "tarefas": tarefas
        })

    conn.close()
    return jsonify(dados)


@app.route("/topico", methods=["POST"])
def criar_topico():
    data = request.get_json()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO topicos (nome) VALUES (?)",
        (data["nome"],)
    )

    topico_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        "id": topico_id,
        "nome": data["nome"],
        "tarefas": []
    })


@app.route("/tarefa", methods=["POST"])
def criar_tarefa():
    data = request.get_json()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tarefas (topico_id, texto, urgencia, concluida)
        VALUES (?, ?, ?, 0)
    """, (
        data["topico_id"],
        data["texto"],
        data["urgencia"]
    ))

    tarefa_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        "id": tarefa_id,
        "texto": data["texto"],
        "urgencia": data["urgencia"],
        "concluida": False
    })


@app.route("/concluir", methods=["POST"])
def concluir_tarefa():
    data = request.get_json()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tarefas
        SET concluida = 1
        WHERE id = ?
    """, (data["tarefa_id"],))

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
