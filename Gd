from flask import Flask, request, jsonify
import banco

app = Flask(__name__)

@app.route("/usuarios", methods=["POST"])
def criar_usuario():
    data = request.json
    nome = data.get("nome")
    email = data.get("email")
    banco.salvar_usuario(nome, email)
    return jsonify({"status": "sucesso"}), 201

@app.route("/usuarios", methods=["GET"])
def pegar_usuarios():
    return jsonify(banco.listar_usuarios())

if __name__ == "__main__":
    app.run(debug=True)
