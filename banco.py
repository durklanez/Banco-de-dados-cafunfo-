import os
import json

# Pasta onde os dados vão ficar
PASTA_BANCO = "banco"
os.makedirs(PASTA_BANCO, exist_ok=True)

def salvar_usuario(nome, email):
    caminho = os.path.join(PASTA_BANCO, f"{email}.json")
    dados = {"nome": nome, "email": email}
    with open(caminho, "w") as f:
        json.dump(dados, f)
    return True

def listar_usuarios():
    usuarios = []
    for arquivo in os.listdir(PASTA_BANCO):
        if arquivo.endswith(".json"):
            with open(os.path.join(PASTA_BANCO, arquivo), "r") as f:
                usuarios.append(json.load(f))
    return usuarios
