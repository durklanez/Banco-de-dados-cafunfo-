from flask import Flask, render_template, request, redirect, session
import json
import datetime

app = Flask(__name__)
app.secret_key = "cafunfo_secret"

USUARIOS_ARQ = "usuarios.json"
LOGS_ARQ = "logs.json"


def ler_usuarios():
    with open(USUARIOS_ARQ, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_usuarios(dados):
    with open(USUARIOS_ARQ, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2)


def registrar_log(email, acao):
    with open(LOGS_ARQ, "r", encoding="utf-8") as f:
        logs = json.load(f)

    logs.append({
        "usuario": email,
        "acao": acao,
        "data": str(datetime.datetime.now())
    })

    with open(LOGS_ARQ, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        usuarios = ler_usuarios()

        novo = {
            "nome": request.form["nome"],
            "email": request.form["email"],
            "senha": request.form["senha"],
            "tipo": "usuario"
        }

        usuarios.append(novo)
        salvar_usuarios(usuarios)

        registrar_log(novo["email"], "criou_conta")

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
        usuarios = ler_usuarios()

        with open(LOGS_ARQ, "r", encoding="utf-8") as f:
            logs = json.load(f)

        return render_template("dashboard_admin.html",
                               total_usuarios=len(usuarios),
                               logs=logs)

    return render_template("dashboard_usuario.html",
                           nome=usuario["nome"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
