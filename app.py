from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash
from banco import conectar, criar_tabela

app = Flask(__name__)

criar_tabela()

@app.route('/cadastro', methods=['POST'])
def cadastro():

    dados = request.get_json(silent=True) or {}

    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')

    if not nome or not email or not senha:
        return jsonify({
            "erro": "Preencha todos os campos"
        }), 400

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        senha_hash = generate_password_hash(senha)

        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha)
            VALUES (%s, %s, %s)
        """, (nome, email, senha_hash))

        conexao.commit()

        return jsonify({
            "mensagem": "Usuário cadastrado com sucesso!"
        }), 201

    except Exception:
        conexao.rollback()
        return jsonify({
            "erro": "Não foi possível realizar o cadastro"
        }), 400

    finally:
        cursor.close()
        conexao.close()


if __name__ == '__main__':
    app.run(debug=True)
