import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tarefas.db")

print("📁 Banco encontrado em:", DB_PATH)

if not os.path.exists(DB_PATH):
    print("❌ Banco NÃO existe")
    exit()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\n📋 TABELAS NO BANCO:")
cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type='table'
""")
tabelas = cursor.fetchall()

for t in tabelas:
    print("-", t[0])

print("\n📌 CONTEÚDO DA TABELA TOPICOS:")
try:
    cursor.execute("SELECT * FROM topicos")
    topicos = cursor.fetchall()
    if not topicos:
        print("⚠️ Nenhum tópico encontrado")
    else:
        for t in topicos:
            print(t)
except Exception as e:
    print("❌ Erro ao ler topicos:", e)

print("\n📌 CONTEÚDO DA TABELA TAREFAS:")
try:
    cursor.execute("SELECT * FROM tarefas")
    tarefas = cursor.fetchall()
    if not tarefas:
        print("⚠️ Nenhuma tarefa encontrada")
    else:
        for t in tarefas:
            print(t)
except Exception as e:
    print("❌ Erro ao ler tarefas:", e)

conn.close()
