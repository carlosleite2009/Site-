import os
import mysql.connector


def conectar():
    # Railway fornece MYSQLHOST, MYSQLPORT, MYSQLUSER, MYSQLPASSWORD e MYSQLDATABASE.
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST") or os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("MYSQLPORT") or os.getenv("DB_PORT", "3306")),
        user=os.getenv("MYSQLUSER") or os.getenv("DB_USER", "root"),
        password=os.getenv("MYSQLPASSWORD") or os.getenv("DB_PASSWORD", ""),
        database=os.getenv("MYSQLDATABASE") or os.getenv("DB_NAME", "sistema_solicitacoes"),
        connection_timeout=15
    )


def criar_tabela():
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(150) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                login VARCHAR(100) NOT NULL UNIQUE,
                senha VARCHAR(255) NOT NULL,
                criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solicitacoes (
                id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(150) NOT NULL,
                titulo VARCHAR(200) NOT NULL,
                descricao TEXT NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'Pendente',
                criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conexao.commit()
    except mysql.connector.Error:
        conexao.rollback()
        raise
    finally:
        cursor.close()
        conexao.close()
