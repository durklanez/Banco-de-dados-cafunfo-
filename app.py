from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "cafunfo_secret"
app.permanent_session_lifetime = timedelta(minutes=30)

DATABASE = "cafunfo.db"


# -----------------------
# CONEXÃO
# -----------------------
def conectar():
    return sqlite3.connect(DATABASE)


# -----------------------
# CRIAR BANCO AUTOMATICAMENTE
# -----------------------
def criar_banco():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT UNIQUE,
        senha TEXT,
        tipo TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        acao TEXT,
        data TEXT
    )
    """)

    # cria admin padrão se não existir
    c.execute("SELECT * FROM usuarios WHERE email=?", ("admin@cafunfo.com",))
    if not c.fetchone():
        c.execute("INSERT INTO usuarios (nome,email,senha,tipo) VALUES (?,?,?,?)",
                  ("Durk", "admin@cafunfo.com", "123456", "admin"))

    conn.commit()
    conn.close()


# 🔥 IMPORTANTE: Executa sempre
criar_banco()


# -----------------------
# REGISTRAR LOG
# -----------------------
def registrar_log(email, acao):
    conn = conectar()
    c = conn.cursor()
    c.execute("INSERT INTO logs (usuario,acao,data) VALUES (?,?,?)",
              (email, acao, str(datetime.now())))
    conn.commit()
    conn.close()


# -----------------------
# ROTAS
# -----------------------

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        conn = conectar()
        c = conn.cursor()

        try:
            c.execute("INSERT INTO usuarios (nome,email,senha,tipo) VALUES (?,?,?,?)",
                      (nome, email, senha, "usuario"))
            conn.commit()
            registrar_log(email, "criou_conta")
        except:
            conn.close()
            return "Email já existe!"

        conn.close()
        return redirect("/login")

    return render_template("registrar.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conn = conectar()
        c = conn.cursor()

        c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
        usuario = c.fetchone()
        conn.close()

        if usuario:
            session.permanent = True
            session["usuario"] = {
                "id": usuario[0],
                "nome": usuario[1],
                "email": usuario[2],
                "tipo": usuario[4]
            }
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
        conn = conectar()
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM usuarios")
        total = c.fetchone()[0]

        c.execute("SELECT usuario, acao, data FROM logs ORDER BY id DESC")
        dados = c.fetchall()

        logs = []
        for l in dados:
            logs.append({
                "usuario": l[0],
                "acao": l[1],
                "data": l[2]
            })

        conn.close()

        return render_template("dashboard_admin.html",
                               total_usuarios=total,
                               logs=logs)

    return render_template("dashboard_usuario.html",
                           nome=usuario["nome"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run()
