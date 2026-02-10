from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Rota principal (abre o site)
@app.route("/")
def home():
    return render_template("index.html")

# API teste (status do banco)
@app.route("/api/status")
def status():
    return jsonify({
        "status": "ok",
        "mensagem": "Banco de dados Cafunfo ativo"
    })

# Exemplo de API para cadastrar dados
@app.route("/api/cadastrar", methods=["POST"])
def cadastrar():
    dados = request.json

    nome = dados.get("nome")
    produto = dados.get("produto")

    return jsonify({
        "status": "sucesso",
        "nome": nome,
        "produto": produto
    })

if __name__ == "__main__":
    app.run(debug=True)
