from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import banco

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/usuarios", methods=["GET"])
def listar():
    return jsonify(banco.listar_usuarios())
