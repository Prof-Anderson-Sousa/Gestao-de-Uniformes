import bcrypt
from banco import conectar
from psycopg2 import errors

def hash_senha(senha):
    # Gera um hash seguro com salt
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

def verificar_senha(senha_digitada, senha_hash):
    # Verifica se a senha digitada corresponde ao hash armazenado
    return bcrypt.checkpw(senha_digitada.encode(), senha_hash.encode())

def criar_usuario(usuario, senha, nivel):
    conn = conectar()
    cursor = conn.cursor()
    senha_hash = hash_senha(senha)
    try:
        cursor.execute(
            "INSERT INTO usuarios (usuario, senha, nivel) VALUES (%s, %s, %s)",
            (usuario, senha_hash, nivel)
        )
        conn.commit()
        print(f"[INFO] Usuário '{usuario}' criado com sucesso.")
        return True
    except errors.UniqueViolation:
        conn.rollback()
        print(f"[ERRO] Usuário '{usuario}' já existe.", flush=True)
        return False
    except Exception as e:
        conn.rollback()
        print(f"[ERRO inesperado] ao criar usuário '{usuario}': {e}", flush=True)
        return False
    finally:
        cursor.close()
        conn.close()

def validar_login(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT senha FROM usuarios WHERE usuario = %s", (usuario,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        senha_hash = resultado[0]
        return verificar_senha(senha, senha_hash)
    return False
