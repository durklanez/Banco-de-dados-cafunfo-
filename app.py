from flask import Flask, jsonify, request, render_template
import json

app = Flask(__name__)

ARQUIVO_BANCO = "banco.json"

def ler_banco():
    with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_banco(dados):
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

@app.route("/")
def home():
    return render_template("index.html")

# ➕ Criar vendedor
@app.route("/api/vendedor", methods=["POST"])
def criar_vendedor():
    dados = request.json
    banco = ler_banco()

    banco["vendedores"].append({
        "nome": dados["nome"],
        "produto": dados["produto"],
        "telefone": dados["telefone"]
    })

    salvar_banco(banco)

    return jsonify({"status": "ok", "mensagem": "Vendedor salvo"})

# 📄 Listar vendedores
@app.route("/api/vendedores")
def listar_vendedores():
    banco = ler_banco()
    return jsonify(banco["vendedores"])
