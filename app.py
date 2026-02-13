from flask import Flask, render_template, request, redirect, session
import json
import datetime
import os
from minio import Minio
from banco import ler_usuarios, salvar_usuarios, registrar_log

app = Flask(__name__)
app.secret_key = "cafunfo_secret"

# Configuração MinIO (Cafunfo Cloud)
MINIO_CLIENT = Minio(
    "localhost:9000",      # Troque para URL do MinIO real se estiver na nuvem
    access_key="admin",
    secret_key="senha123",
    secure=False
)
BUCKET_NAME = "arquivos"

if not MINIO_CLIENT.bucket_exists(BUCKET_NAME):
    MINIO_CLIENT.make_bucket(BUCKET_NAME)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        usuarios = ler_usuarios()
        email = request.form["email"]

        # Bloquear email duplicado
        if any(u["email"] == email for u in usuarios):
            return "E-mail já cadastrado!"

        novo_usuario = {
            "nome": request.form["nome"],
            "email": email,
            "senha": request.form["senha"],
            "tipo": "usuario"
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

    if usuario["tipo"] == "admin":
        with open("logs.json", "r", encoding="utf-8") as f:
            logs = json.load(f)
        total_usuarios = len(ler_usuarios())
        return render_template("dashboard_admin.html",
                               total_usuarios=total_usuarios,
                               logs=logs)
    else:
        return render_template("dashboard_usuario.html",
                               nome=usuario["nome"])


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "usuario" not in session:
        return redirect("/login")

    if request.method == "POST":
        arquivo = request.files["arquivo"]
        if arquivo:
            MINIO_CLIENT.put_object(
                BUCKET_NAME,
                arquivo.filename,
                arquivo,
                length=os.fstat(arquivo.fileno()).st_size
            )
            registrar_log(session["usuario"]["email"], f"upload_arquivo:{arquivo.filename}")
            return f"Arquivo {arquivo.filename} enviado com sucesso!"
    return render_template("upload.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
