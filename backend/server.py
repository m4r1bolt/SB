from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import os

app = Flask(__name__, static_folder="frontend")  # Define a pasta do frontend

CSV_FILE = "cadastro_usuarios.csv"

# Criar o arquivo CSV se não existir
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["CPF", "Nome", "E-mail", "Telefone", "Esporte", "Objeto1", "Objeto2", "Objeto3", "Pontuacao"])
    df.to_csv(CSV_FILE, index=False)

OBJETOS_VALOR_REAL = {
    "Objeto1":50,
    "Objeto2":75,
    "Objeto3":100
}

def calcular_pontuacao(palpites):
    pontuacao_total = 0
    for objeto, valor_palpite in palpites.items():
        if objeto in OBJETOS_VALOR_REAL and valor_palpite is not None:
            try:
                valor_palpite = float(valor_palpite)
                valor_real = OBJETOS_VALOR_REAL[objeto]

                pontuacao = 10 * max(0, 1 - abs(valor_palpite - valor_real)/ valor_real)
                pontuacao_total += pontuacao
            
            except ValueError:
                pass

    return round(pontuacao_total, 2)


@app.route("/")
def serve_index():
    return send_from_directory("frontend", "cadastro.html")  # Página inicial

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("frontend", path)  # Servir outros arquivos

@app.route("/api/palpite", methods=["POST"])
def registrar_aposta():
    """Registra a aposta de um usuário, mesmo que ele não tenha sido cadastrado antes."""
    dados = request.json
    cpf = dados.get("cpf")
    nome = dados.get("nome", "Desconhecido")
    email = dados.get("email", "")
    telefone = dados.get("telefone", "")
    esporte = dados.get("esporte", "")
    objeto1 = dados.get("objeto1")
    objeto2 = dados.get("objeto2")
    objeto3 = dados.get("objeto3")

    if not cpf:
        return jsonify({"error": "CPF é obrigatório"}), 400

    df = pd.read_csv(CSV_FILE)
    palpites = {"Objeto1": objeto1, "Objeto2": objeto2, "Objeto3": objeto3}
    pontuacao = calcular_pontuacao(palpites)

    if cpf in df["CPF"].values:
        df.loc[df["CPF"] == cpf, ["Objeto1", "Objeto2", "Objeto3", "Pontuacao"]] = [objeto1, objeto2, objeto3, pontuacao]
    else:
        novo_usuario = pd.DataFrame([[cpf, nome, email, telefone, esporte, objeto1, objeto2, objeto3]],
                                    columns=["CPF", "Nome", "E-mail", "Telefone", "Esporte", "Objeto1", "Objeto2", "Objeto3"])
        df = pd.concat([df, novo_usuario], ignore_index=True)

    df.to_csv(CSV_FILE, index=False)

    return jsonify({"message": "Aposta registrada com sucesso!"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=10000)
