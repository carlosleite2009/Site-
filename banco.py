import os
import mysql.connector

def conectar():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=int(os.getenv("MYSQLPORT", 3306))
    )


def criar_tabela():
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(150) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                senha VARCHAR(255) NOT NULL
            )
        """)

        conexao.commit()

    finally:
        cursor.close()
        conexao.close()
