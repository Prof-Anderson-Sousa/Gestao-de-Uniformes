import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox, filedialog
from tkinter import ttk
from tkcalendar import DateEntry
from auth import validar_login, criar_usuario
from sistema_fardamento import iniciar_interface
from banco import inicializar_banco, conectar
from openpyxl import Workbook
import datetime
import os
from pathlib import Path
from devolucao import tela_devolucao
from sistema_fardamento import criar_botao
from sistema_fardamento import COR_VERDE
import bcrypt
import re
import random
import string

def validar_senha(senha: str) -> bool:
    """Valida se a senha é forte:
    - Pelo menos 8 caracteres
    - Pelo menos 1 letra
    - Pelo menos 1 número
    - Pelo menos 1 caractere especial
    """
    if len(senha) < 8:
        return False
    if not re.search(r"[A-Za-z]", senha):
        return False
    if not re.search(r"\d", senha):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):
        return False
    return True

def hash_senha(senha):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

def criar_novo_usuario(janela_pai):
    def salvar():
        novo_user = entry_user.get().strip()
        senha1 = entry_pass.get()
        senha2 = entry_pass_conf.get()
        nivel = nivel_var.get()

        if not novo_user or not senha1 or not senha2 or not nivel:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        if senha1 != senha2:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return

        if not validar_senha(senha1):
            messagebox.showerror(
                "Erro",
                "A senha deve ter no mínimo 8 caracteres e conter letra, número e caractere especial."
            )
            return

        if criar_usuario(novo_user, senha1, nivel):
            messagebox.showinfo("Sucesso", "Usuário criado com sucesso.")
            cadastro.destroy()
        else:
            messagebox.showerror("Erro", "Usuário já existe ou erro ao criar.")

    cadastro = tk.Toplevel(janela_pai)
    cadastro.title("Novo Usuário")
    cadastro.geometry("300x300")
    cadastro.resizable(False, False)

    tk.Label(cadastro, text="Novo Usuário:").pack(pady=5)
    entry_user = tk.Entry(cadastro)
    entry_user.pack(pady=5)

    tk.Label(cadastro, text="Senha:").pack(pady=5)
    entry_pass = tk.Entry(cadastro, show="*")
    entry_pass.pack(pady=5)

    tk.Label(cadastro, text="Confirmar Senha:").pack(pady=5)
    entry_pass_conf = tk.Entry(cadastro, show="*")
    entry_pass_conf.pack(pady=5)

    tk.Label(cadastro, text="Nível:").pack(pady=5)
    nivel_var = tk.StringVar()
    nivel_combo = ttk.Combobox(cadastro, textvariable=nivel_var, values=["admin", "default"], state="readonly")
    nivel_combo.pack(pady=5)
    nivel_combo.current(1)

    tk.Button(cadastro, text="Salvar", command=salvar).pack(pady=10)

def alterar_senha(janela_pai):
    def atualizar():
        usuario = combo_user.get().strip()
        senha_antiga = entry_old.get()
        senha1 = entry_new.get()
        senha2 = entry_conf.get()

        if not usuario or not senha_antiga or not senha1 or not senha2:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT senha FROM usuarios WHERE usuario = %s", (usuario,))
        result = cursor.fetchone()

        if not result:
            messagebox.showerror("Erro", "Usuário não encontrado.")
            conn.close()
            return

        senha_hash = result[0]
        if not bcrypt.checkpw(senha_antiga.encode(), senha_hash.encode()):
            messagebox.showerror("Erro", "Senha antiga incorreta.")
            conn.close()
            return

        if senha1 != senha2:
            messagebox.showerror("Erro", "As novas senhas não coincidem.")
            conn.close()
            return

        if not validar_senha(senha1):
            messagebox.showerror(
                "Erro",
                "A nova senha deve ter no mínimo 8 caracteres e conter letra, número e caractere especial."
            )
            conn.close()
            return

        nova_hash = bcrypt.hashpw(senha1.encode(), bcrypt.gensalt()).decode()
        cursor.execute("UPDATE usuarios SET senha = %s WHERE usuario = %s", (nova_hash, usuario))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Senha atualizada com sucesso.")
        janela.destroy()

    # Buscar usuários no banco
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT usuario FROM usuarios ORDER BY usuario ASC")
    usuarios = [row[0] for row in cursor.fetchall()]
    conn.close()

    janela = tk.Toplevel(janela_pai)
    janela.title("Alterar Senha")
    janela.geometry("320x300")
    janela.resizable(False, False)

    tk.Label(janela, text="Selecione o Usuário:").pack(pady=5)
    combo_user = ttk.Combobox(janela, values=usuarios, width=25, state="readonly")
    combo_user.pack(pady=5)

    tk.Label(janela, text="Senha Antiga:").pack(pady=5)
    entry_old = tk.Entry(janela, show="*")
    entry_old.pack(pady=5)

    tk.Label(janela, text="Nova Senha:").pack(pady=5)
    entry_new = tk.Entry(janela, show="*")
    entry_new.pack(pady=5)

    tk.Label(janela, text="Confirmar Nova Senha:").pack(pady=5)
    entry_conf = tk.Entry(janela, show="*")
    entry_conf.pack(pady=5)

    tk.Button(janela, text="Atualizar", command=atualizar).pack(pady=10)

def excluir_usuario(janela_pai):
    def gerar_captcha():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    captcha_code = gerar_captcha()

    def remover():
        usuario = combo_user.get().strip()
        captcha_input = entry_captcha.get().strip()

        if not usuario:
            messagebox.showwarning("Aviso", "Selecione um usuário válido.")
            return

        if captcha_input != captcha_code:
            messagebox.showerror("Erro", "Captcha incorreto. Tente novamente.")
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE usuario = %s", (usuario,))
        if cursor.rowcount:
            conn.commit()
            messagebox.showinfo("Sucesso", f"Usuário '{usuario}' excluído com sucesso.")
            janela.destroy()
        else:
            messagebox.showerror("Erro", "Usuário não encontrado.")
        conn.close()

    # Buscar usuários no banco (exceto admin)
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT usuario FROM usuarios WHERE usuario != 'admin' ORDER BY usuario ASC")
    usuarios = [row[0] for row in cursor.fetchall()]
    conn.close()

    janela = tk.Toplevel(janela_pai)
    janela.title("Excluir Usuário")
    janela.geometry("320x220")
    janela.resizable(False, False)

    tk.Label(janela, text="Selecione o Usuário:", font=("Segoe UI", 10, "bold")).pack(pady=5)
    combo_user = ttk.Combobox(janela, values=usuarios, width=25, state="readonly")
    combo_user.pack(pady=5)

    tk.Label(janela, text=f"Digite o código: {captcha_code}", font=("Segoe UI", 10, "bold")).pack(pady=5)
    entry_captcha = tk.Entry(janela)
    entry_captcha.pack(pady=5)

    tk.Button(janela, text="Excluir", command=remover).pack(pady=10)

def adicionar_colaborador(janela_pai):
    def salvar():
        nome = entry_nome.get().strip()
        if nome:
            conn = conectar()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO colaboradores (nome) VALUES (%s)", (nome,))
                conn.commit()
                messagebox.showinfo("Sucesso", f"Colaborador '{nome}' adicionado com sucesso.")
                janela.destroy()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Erro", f"Não foi possível adicionar: {e}")
            conn.close()
        else:
            messagebox.showwarning("Aviso", "Digite um nome válido.")

    janela = tk.Toplevel(janela_pai)
    janela.title("Adicionar Colaborador")
    janela.geometry("300x140")
    tk.Label(janela, text="Nome do Colaborador:").pack(pady=10)
    entry_nome = tk.Entry(janela, width=30)
    entry_nome.pack(pady=5)
    tk.Button(janela, text="Salvar", command=salvar).pack(pady=10)

def remover_colaborador(janela_pai):
    def excluir():
        nome = combo_colaborador.get()
        if nome:
            confirm = messagebox.askyesno(
                "Confirmação",
                f"Tem certeza que deseja excluir o colaborador '{nome}'?"
            )
            if confirm:
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM colaboradores WHERE nome = %s", (nome,))
                if cursor.rowcount:
                    conn.commit()
                    messagebox.showinfo("Sucesso", f"Colaborador '{nome}' removido.")
                    janela.destroy()
                else:
                    messagebox.showerror("Erro", "Colaborador não encontrado.")
                conn.close()
        else:
            messagebox.showwarning("Aviso", "Selecione um colaborador.")

    # Busca os colaboradores atuais no banco
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM colaboradores ORDER BY nome ASC")
    colaboradores = [row[0] for row in cursor.fetchall()]
    conn.close()

    janela = tk.Toplevel(janela_pai)
    janela.title("Remover Colaborador")
    janela.geometry("320x160")
    janela.resizable(False, False)

    tk.Label(janela, text="Selecione o Colaborador:", font=("Segoe UI", 10, "bold")).pack(pady=10)

    combo_colaborador = ttk.Combobox(janela, values=colaboradores, width=30, state="readonly")
    combo_colaborador.pack(pady=5)

    tk.Button(janela, text="Excluir", command=excluir).pack(pady=10)

def exportar_excel_por_periodo(janela_pai):
    def exportar():
        data_ini = entry_ini.get()
        data_fim = entry_fim.get()

        try:
            d_ini = datetime.datetime.strptime(data_ini, "%d/%m/%Y").strftime("%Y-%m-%d")
            d_fim = datetime.datetime.strptime(data_fim, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Data inválida. Use o seletor de datas.")
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nome, tipo, codigo, data_retirada, hora_retirada, data_devolucao, hora_devolucao
            FROM registros
            WHERE data_retirada BETWEEN %s AND %s
        """, (d_ini, d_fim))
        dados = cursor.fetchall()
        conn.close()

        if not dados:
            messagebox.showinfo("Aviso", "Nenhum registro encontrado no período.")
            return

        wb = Workbook()
        ws = wb.active
        ws.title = "Registros"
        ws.append(["Nome", "Tipo", "Código", "Data Retirada", "Hora Retirada", "Data Devolução", "Hora Devolução"])
        for row in dados:
            ws.append(row)

        downloads_dir = str(Path.home() / "Downloads")
        nome_arquivo_padrao = os.path.join(downloads_dir, f"registros_{d_ini}_a_{d_fim}.xlsx")

        caminho = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Planilha Excel", "*.xlsx")],
            initialdir=downloads_dir,
            initialfile=os.path.basename(nome_arquivo_padrao),
            title="Salvar como"
        )

        if caminho:
            wb.save(caminho)
            messagebox.showinfo("Sucesso", f"Exportado para {caminho}")
            janela.destroy()

    janela = tk.Toplevel(janela_pai)
    janela.title("Exportar para Excel")
    janela.geometry("300x200")
    janela.resizable(False, False)

    tk.Label(janela, text="Data Inicial (dd/mm/aaaa):").pack(pady=5)
    entry_ini = DateEntry(janela, date_pattern='dd/mm/yyyy', width=18)
    entry_ini.pack(pady=5)

    tk.Label(janela, text="Data Final (dd/mm/aaaa):").pack(pady=5)
    entry_fim = DateEntry(janela, date_pattern='dd/mm/yyyy', width=18)
    entry_fim.pack(pady=5)

    tk.Button(janela, text="Exportar", command=exportar).pack(pady=10)

def criar_botao_grid(janela, comando, icone_path):
    frame = tk.Frame(janela, bg="#f5f5f5", width=150, height=150, highlightthickness=0)
    frame.grid_propagate(False)

    # Ícone como botão
    img = Image.open(icone_path).resize((150, 150))
    icon = ImageTk.PhotoImage(img)

    btn = tk.Button(
        frame,
        image=icon,
        command=comando,
        relief="flat",
        bd=0,
        highlightthickness=0,
        bg="#f5f5f5",
        activebackground="#f5f5f5"
    )
    btn.image = icon
    btn.pack(expand=True, fill="both", padx=0, pady=0)

    return frame

def menu_admin(usuario):
    admin_win = tk.Tk()
    admin_win.title("Painel do Administrador")
    admin_win.geometry("850x600")  # <-- define o tamanho da janela
    admin_win.configure(bg="#f5f5f5")

    ttk.Label(
        admin_win,
        text=f"Bem-vindo, {usuario.capitalize()}!",
        font=("Segoe UI", 14, "bold"),
        background="#f5f5f5"
    ).pack(pady=10)

    grid_frame = tk.Frame(admin_win, bg="#f5f5f5")
    grid_frame.pack(pady=20)

    botoes = [
    (lambda: criar_novo_usuario(admin_win), "icons/criar user.png"),
    (lambda: alterar_senha(admin_win), "icons/alterar senha.png"),
    (lambda: excluir_usuario(admin_win), "icons/excluir user.png"),
    (lambda: exportar_excel_por_periodo(admin_win), "icons/exportar excel.png"),
    (lambda: [admin_win.destroy(), iniciar_interface(usuario)], "icons/registrar retirada.png"),
    (lambda: [admin_win.destroy(), tela_devolucao(menu_admin, usuario)], "icons/registrar devolucao.png"),
    (lambda: adicionar_colaborador(admin_win), "icons/adicionar colaborador.png"),
    (lambda: remover_colaborador(admin_win), "icons/remover colaborador.png")
    ]

    for i, (cmd, icone) in enumerate(botoes):
        r = i // 4
        c = i % 4
        criar_botao_grid(grid_frame, cmd, icone).grid(row=r, column=c, padx=20, pady=20)

    admin_win.mainloop()

def menu_usuario(usuario):
    user_win = tk.Tk()
    user_win.title("Menu do Usuário")
    user_win.geometry("300x220")
    user_win.resizable(False, False)

    ttk.Label(user_win, text=f"Bem-vindo, {usuario.capitalize()}!", font=("Segoe UI", 12, "bold")).pack(pady=20)

    criar_botao(user_win, "Registrar Retirada", lambda: [user_win.destroy(), iniciar_interface(usuario)], COR_VERDE, "white").pack(pady=10)
    criar_botao(user_win, "Registrar Devolução", lambda: [user_win.destroy(), tela_devolucao(menu_usuario, usuario)], COR_VERDE, "white").pack(pady=10)

    user_win.mainloop()


def tela_login():
    inicializar_banco()

    def tentar_login():
        usuario = entry_usuario.get()
        senha = entry_senha.get()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nivel FROM usuarios WHERE usuario = %s", (usuario,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado and validar_login(usuario, senha):
            nivel = resultado[0]
            login_win.destroy()
            if nivel == "admin":
                menu_admin(usuario)
            else:
                menu_usuario(usuario)
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos")

    login_win = tk.Tk()
    login_win.title("Login - Fardamento")
    login_win.geometry("300x180")
    login_win.resizable(False, False)

    tk.Label(login_win, text="Usuário:").pack(pady=5)
    entry_usuario = tk.Entry(login_win)
    entry_usuario.pack(pady=5)

    tk.Label(login_win, text="Senha:").pack(pady=5)
    entry_senha = tk.Entry(login_win, show="*")
    entry_senha.pack(pady=5)

    tk.Button(login_win, text="Entrar", command=tentar_login).pack(pady=10)

    login_win.mainloop()

if __name__ == "__main__":
    tela_login()