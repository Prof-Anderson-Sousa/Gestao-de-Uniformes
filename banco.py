import psycopg2
from psycopg2 import sql, errors
import bcrypt
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Dados de conexão com o PostgreSQL
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT")
}

def conectar():
    return psycopg2.connect(**DB_CONFIG)

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()

    # Tabela de usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        nivel TEXT DEFAULT 'usuario'
    )
    """)

    # Criar usuário admin padrão
    senha_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
    try:
        cursor.execute(
            "INSERT INTO usuarios (usuario, senha, nivel) VALUES (%s, %s, %s)", 
            ("admin", senha_hash, "admin")
        )
    except errors.UniqueViolation:
        conn.rollback()
        print("Usuário 'admin' já existe.")
    except Exception as e:
        conn.rollback()
        print(f"Erro ao criar usuário admin: {e}")

    # Tabela de registros de fardamento
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registros (
        id SERIAL PRIMARY KEY,
        nome TEXT,
        tipo TEXT,
        codigo TEXT,
        data_retirada TEXT,
        hora_retirada TEXT,
        data_devolucao TEXT,
        hora_devolucao TEXT
    )
    """)

        # Tabela de colaboradores
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS colaboradores (
        id SERIAL PRIMARY KEY,
        nome TEXT UNIQUE NOT NULL
    )
    """)


    conn.commit()
    cursor.close()
    conn.close()