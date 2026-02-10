from flask import Flask, request, jsonify
from flask_cors import CORS
import banco

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return {
        "status": "ok",
        "mensagem": "Banco de dados Cafunfo ativo"
    }

@app.route("/usuarios", methods=["GET"])
def listar():
    return jsonify(banco.listar_usuarios())
