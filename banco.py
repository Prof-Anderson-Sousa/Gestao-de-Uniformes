import sqlite3
from pathlib import Path
import hashlib

DB_PATH = r"\\s-81-1-0001\Work$\APP\base fardas\registro_fardamento.db"

def conectar():
    return sqlite3.connect(DB_PATH)

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()

    # Tabela de usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        nivel TEXT DEFAULT 'usuario'
    )
    """)

    # Criar usuário admin padrão
    senha_hash = hashlib.sha256("admin123".encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO usuarios (usuario, senha, nivel) VALUES (?, ?, ?)", ("admin", senha_hash, "admin"))
    except sqlite3.IntegrityError:
        pass  # Usuário já existe

    # Tabela de registros de fardamento
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        tipo TEXT,
        codigo TEXT,
        data_retirada TEXT,
        hora_retirada TEXT,
        data_devolucao TEXT,
        hora_devolucao TEXT
    )
    """)

    conn.commit()
    conn.close()