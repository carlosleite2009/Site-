import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from mysql.connector import IntegrityError, Error as MySQLError
from banco import conectar, criar_tabela

app = Flask(__name__)
origens = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]
CORS(app, resources={r"/*": {"origins": origens}})

try:
    criar_tabela()
except MySQLError:
    app.logger.exception("Falha ao criar/verificar tabelas MySQL")


@app.get("/")
def inicio():
    return jsonify({"mensagem": "API do Sistema de Registro de Solicitações está online."})


@app.get("/health")
def health():
    try:
        conexao = conectar()
        conexao.close()
        return jsonify({"status": "ok", "banco": "conectado"}), 200
    except MySQLError:
        app.logger.exception("Falha na conexão MySQL")
        return jsonify({"status": "erro", "banco": "indisponível"}), 503


@app.post("/cadastro")
def cadastro():
    dados = request.get_json(silent=True) or {}
    nome = (dados.get("nome") or "").strip()
    email = (dados.get("email") or "").strip().lower()
    login = (dados.get("login") or "").strip()
    senha = dados.get("senha") or ""
    if not all([nome, email, login, senha]):
        return jsonify({"erro": "Preencha todos os campos."}), 400

    conexao = cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, login, senha) VALUES (%s, %s, %s, %s)",
            (nome, email, login, generate_password_hash(senha))
        )
        conexao.commit()
        return jsonify({"mensagem": "Usuário cadastrado com sucesso!"}), 201
    except IntegrityError:
        if conexao: conexao.rollback()
        return jsonify({"erro": "Este e-mail ou nome de usuário já está cadastrado."}), 409
    except MySQLError:
        if conexao: conexao.rollback()
        app.logger.exception("Erro no cadastro")
        return jsonify({"erro": "Não foi possível realizar o cadastro. Verifique o banco."}), 500
    finally:
        if cursor: cursor.close()
        if conexao and conexao.is_connected(): conexao.close()


@app.post("/login")
def login():
    dados = request.get_json(silent=True) or {}
    usuario = (dados.get("login") or "").strip()
    senha = dados.get("senha") or ""
    if not usuario or not senha:
        return jsonify({"erro": "Informe o login e a senha."}), 400

    conexao = cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, senha FROM usuarios WHERE login = %s LIMIT 1", (usuario,))
        registro = cursor.fetchone()
        if not registro or not check_password_hash(registro["senha"], senha):
            return jsonify({"erro": "Login ou senha incorretos."}), 401
        return jsonify({
            "mensagem": "Login realizado com sucesso!",
            "id": registro["id"],
            "nome": registro["nome"]
        }), 200
    except MySQLError:
        app.logger.exception("Erro no login")
        return jsonify({"erro": "Não foi possível realizar o login. Verifique o servidor."}), 500
    finally:
        if cursor: cursor.close()
        if conexao and conexao.is_connected(): conexao.close()


@app.route("/solicitacoes", methods=["GET", "POST"])
def solicitacoes():
    conexao = cursor = None
    try:
        conexao = conectar()
        if request.method == "POST":
            dados = request.get_json(silent=True) or {}
            nome = (dados.get("nome") or "").strip()
            titulo = (dados.get("titulo") or "").strip()
            descricao = (dados.get("descricao") or "").strip()
            if not all([nome, titulo, descricao]):
                return jsonify({"erro": "Informe nome, título e descrição."}), 400
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO solicitacoes (nome, titulo, descricao, status) VALUES (%s, %s, %s, %s)",
                (nome, titulo, descricao, "Pendente")
            )
            conexao.commit()
            return jsonify({"mensagem": "Solicitação registrada com sucesso!", "id": cursor.lastrowid}), 201

        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, titulo, descricao, status, criado_em FROM solicitacoes ORDER BY criado_em DESC")
        itens = cursor.fetchall()
        for item in itens:
            if item.get("criado_em"):
                item["criado_em"] = item["criado_em"].isoformat()
        return jsonify(itens), 200
    except MySQLError:
        if conexao: conexao.rollback()
        app.logger.exception("Erro nas solicitações")
        return jsonify({"erro": "Não foi possível processar as solicitações."}), 500
    finally:
        if cursor: cursor.close()
        if conexao and conexao.is_connected(): conexao.close()


@app.route("/solicitacoes/<int:solicitacao_id>", methods=["PUT", "DELETE"])
def gerenciar_solicitacao(solicitacao_id):
    conexao = cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        if request.method == "PUT":
            dados = request.get_json(silent=True) or {}
            status = (dados.get("status") or "").strip()
            if not status:
                return jsonify({"erro": "Informe o novo status."}), 400
            cursor.execute("UPDATE solicitacoes SET status = %s WHERE id = %s", (status, solicitacao_id))
            conexao.commit()
            if cursor.rowcount == 0:
                return jsonify({"erro": "Solicitação não encontrada."}), 404
            return jsonify({"mensagem": "Status atualizado com sucesso!"}), 200

        cursor.execute("DELETE FROM solicitacoes WHERE id = %s", (solicitacao_id,))
        conexao.commit()
        if cursor.rowcount == 0:
            return jsonify({"erro": "Solicitação não encontrada."}), 404
        return jsonify({"mensagem": "Solicitação excluída com sucesso!"}), 200
    except MySQLError:
        if conexao: conexao.rollback()
        app.logger.exception("Erro ao alterar solicitação")
        return jsonify({"erro": "Não foi possível concluir a operação."}), 500
    finally:
        if cursor: cursor.close()
        if conexao and conexao.is_connected(): conexao.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
