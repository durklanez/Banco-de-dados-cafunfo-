import json
import datetime

USUARIOS_ARQ = "usuarios.json"
LOGS_ARQ = "logs.json"


def ler_usuarios():
    try:
        with open(USUARIOS_ARQ, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def salvar_usuarios(dados):
    with open(USUARIOS_ARQ, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2)


def registrar_log(email, acao):
    try:
        with open(LOGS_ARQ, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        logs = []

    logs.append({
        "usuario": email,
        "acao": acao,
        "data": str(datetime.datetime.now())
    })

    with open(LOGS_ARQ, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)
