from flask import Flask, render_template, request, redirect, session, send_file, jsonify
import sqlite3
import datetime
import io
import os
import uuid
from google.cloud import storage

# =========================================
# 🚀 CONFIGURAÇÕES
# =========================================

app = Flask(__name__)
app.secret_key = "cafunfo_super_secret_key"

DB_FILE = "cafunfo.db"
GCS_BUCKET_NAME = "SEU_BUCKET_NO_GCS"  # <--- troque pelo nome do bucket

# =========================================
# 🔧 Funções Auxiliares
# =========================================

def criar_banco():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # tabela de usuários
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id TEXT PRIMARY KEY,
            nome TEXT,
            email TEXT UNIQUE,
            senha TEXT,
            api_key TEXT
        )
    ''')
    # tabela de logs
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id TEXT PRIMARY KEY,
            usuario TEXT,
            acao TEXT,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

def registrar_usuario(nome, email, senha):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    user_id = str(uuid.uuid4())
    api_key = str(uuid.uuid4())
    c.execute('INSERT INTO usuarios VALUES (?, ?, ?, ?, ?)',
              (user_id, nome, email, senha, api_key))
    conn.commit()
    conn.close()
    registrar_log(email, "criou_conta")
    return api_key

def registrar_log(usuario, acao):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    log_id = str(uuid.uuid4())
    data = str(datetime.datetime.now())
    c.execute('INSERT INTO logs VALUES (?, ?, ?, ?)',
              (log_id, usuario, acao, data))
    conn.commit()
    conn.close()

def ler_usuarios():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, nome, email, senha, api_key FROM usuarios')
    usuarios = [{"id": row[0], "nome": row[1], "email": row[2], "senha": row[3], "api_key": row[4]} for row in c.fetchall()]
    conn.close()
    return usuarios

def ler_logs():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT usuario, acao, data FROM logs ORDER BY data DESC')
    logs = [{"usuario": row[0], "acao": row[1], "data": row[2]} for row in c.fetchall()]
    conn.close()
    return logs

def backup_gcs():
    """Faz backup do banco SQLite no Google Cloud Storage"""
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(f"backup_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.db")
    blob.upload_from_filename(DB_FILE)
    print("Backup enviado para GCS!")

# Inicializa banco
criar_banco()

# =========================================
# 🌐 ROTAS WEB
# =========================================

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        email = request.form["email"]
        usuarios = ler_usuarios()
        if any(u["email"] == email for u in usuarios):
            return "Email já existe"
        nome = request.form["nome"]
        senha = request.form["senha"]
        registrar_usuario(nome, email, senha)
        return redirect("/login")
    return render_template("registrar.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        usuarios = ler_usuarios()
        for u in usuarios:
            if u["email"] == email and u["senha"] == senha:
                session["usuario"] = u
                registrar_log(email, "login")
                return redirect("/dashboard")
        return "Login inválido"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect("/login")
    usuario = session["usuario"]
    usuarios = ler_usuarios()
    logs = ler_logs()
    return render_template("dashboard.html",
                           usuario=usuario,
                           total_usuarios=len(usuarios),
                           logs=logs)

@app.route("/download_db")
def download_db():
    if "usuario" not in session:
        return redirect("/login")
    json_bytes = io.BytesIO()
    data = {
        "usuarios": ler_usuarios(),
        "logs": ler_logs()
    }
    json_bytes.write(json.dumps(data, indent=2).encode("utf-8"))
    json_bytes.seek(0)
    return send_file(json_bytes, download_name="cafunfo_backup.json", as_attachment=True, mimetype="application/json")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# =========================================
# ▶ INICIALIZAÇÃO
# =========================================

if __name__ == "__main__":
    # Faz backup automático ao iniciar (pode agendar usando cronjob depois)
    backup_gcs()
    app.run(debug=True)
