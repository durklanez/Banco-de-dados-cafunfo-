from flask import Flask, render_template, request, redirect, session, send_file, jsonify
import json
import datetime
import io
import os
import uuid

# =========================================
# 🚀 CAFUNFO API PLATFORM
# =========================================

app = Flask(__name__)
app.secret_key = "cafunfo_super_secret_key"

USUARIOS_ARQ = "usuarios.json"
LOGS_ARQ = "logs.json"

# =========================================
# 🔧 Funções Auxiliares
# =========================================

def inicializar_arquivos():
    if not os.path.exists(USUARIOS_ARQ):
        with open(USUARIOS_ARQ, "w", encoding="utf-8") as f:
            json.dump([], f)

    if not os.path.exists(LOGS_ARQ):
        with open(LOGS_ARQ, "w", encoding="utf-8") as f:
            json.dump([], f)

def ler_usuarios():
    with open(USUARIOS_ARQ, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_usuarios(dados):
    with open(USUARIOS_ARQ, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2)

def registrar_log(usuario, acao):
    with open(LOGS_ARQ, "r", encoding="utf-8") as f:
        logs = json.load(f)

    logs.append({
        "usuario": usuario,
        "acao": acao,
        "data": str(datetime.datetime.now())
    })

    with open(LOGS_ARQ, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)

# Inicializa arquivos automaticamente
inicializar_arquivos()

# =========================================
# 🌐 ROTAS WEB
# =========================================

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        usuarios = ler_usuarios()
        email = request.form["email"]

        if any(u["email"] == email for u in usuarios):
            return "Email já existe"

        novo_usuario = {
            "id": str(uuid.uuid4()),
            "nome": request.form["nome"],
            "email": email,
            "senha": request.form["senha"],
            "api_key": str(uuid.uuid4())
        }

        usuarios.append(novo_usuario)
        salvar_usuarios(usuarios)
        registrar_log(email, "criou_conta")

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

    with open(LOGS_ARQ, "r", encoding="utf-8") as f:
        logs = json.load(f)

    return render_template("dashboard.html",
                           usuario=usuario,
                           total_usuarios=len(usuarios),
                           logs=logs)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/download_db")
def download_db():
    if "usuario" not in session:
        return redirect("/login")

    db_data = {
        "usuarios": ler_usuarios(),
        "logs": json.load(open(LOGS_ARQ, "r", encoding="utf-8"))
    }

    json_bytes = io.BytesIO()
    json_bytes.write(json.dumps(db_data, indent=2).encode("utf-8"))
    json_bytes.seek(0)

    return send_file(
        json_bytes,
        download_name="cafunfo_database.json",
        as_attachment=True,
        mimetype="application/json"
    )

# =========================================
# 🔥 ROTAS API PROFISSIONAIS
# =========================================

@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify({
        "platform": "CAFUNFO API PLATFORM",
        "status": "online",
        "data": str(datetime.datetime.now())
    })

@app.route("/api/usuarios", methods=["GET"])
def api_usuarios():
    api_key = request.headers.get("x-api-key")

    usuarios = ler_usuarios()

    for u in usuarios:
        if u["api_key"] == api_key:
            return jsonify({
                "usuarios": usuarios
            })

    return jsonify({"erro": "API KEY inválida"}), 403

@app.route("/api/login", methods=["POST"])
def api_login():
    dados = request.json
    email = dados.get("email")
    senha = dados.get("senha")

    usuarios = ler_usuarios()

    for u in usuarios:
        if u["email"] == email and u["senha"] == senha:
            return jsonify({
                "status": "sucesso",
                "nome": u["nome"],
                "email": u["email"],
                "api_key": u["api_key"]
            })

    return jsonify({"status": "erro"}), 401

# =========================================
# ▶ INICIALIZAÇÃO
# =========================================

if __name__ == "__main__":
    app.run(debug=True)
