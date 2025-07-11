import hashlib
from banco import conectar

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def criar_usuario(usuario, senha, nivel='default'):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (usuario, senha, nivel) VALUES (?, ?, ?)",
                       (usuario, hash_senha(senha), nivel))
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        conn.close()

def validar_login(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?",
                   (usuario, hash_senha(senha)))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None