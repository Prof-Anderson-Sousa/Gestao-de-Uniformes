import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from tkcalendar import DateEntry
from auth import validar_login, criar_usuario
from sistema_fardamento import iniciar_interface
from banco import inicializar_banco, conectar
import hashlib
from openpyxl import Workbook
import datetime
import os
from pathlib import Path
from devolucao import tela_devolucao
from sistema_fardamento import criar_botao
from sistema_fardamento import COR_VERDE

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def criar_novo_usuario(janela_pai):
    def salvar():
        novo_user = entry_user.get()
        nova_senha = entry_pass.get()
        nivel = nivel_var.get()

        if novo_user and nova_senha and nivel:
            if criar_usuario(novo_user, nova_senha, nivel):
                messagebox.showinfo("Sucesso", "Usuário criado com sucesso.")
                cadastro.destroy()
            else:
                messagebox.showerror("Erro", "Usuário já existe ou erro ao criar.")
        else:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")

    cadastro = tk.Toplevel(janela_pai)
    cadastro.title("Novo Usuário")
    cadastro.geometry("280x240")
    cadastro.resizable(False, False)

    tk.Label(cadastro, text="Novo Usuário:").pack(pady=5)
    entry_user = tk.Entry(cadastro)
    entry_user.pack(pady=5)

    tk.Label(cadastro, text="Senha:").pack(pady=5)
    entry_pass = tk.Entry(cadastro, show="*")
    entry_pass.pack(pady=5)

    tk.Label(cadastro, text="Nível:").pack(pady=5)
    nivel_var = tk.StringVar()
    nivel_combo = ttk.Combobox(cadastro, textvariable=nivel_var, values=["admin", "default"], state="readonly")
    nivel_combo.pack(pady=5)
    nivel_combo.current(1)  # Padrão selecionado inicialmente

    tk.Button(cadastro, text="Salvar", command=salvar).pack(pady=10)

def alterar_senha(janela_pai):
    def atualizar():
        usuario = entry_user.get()
        nova_senha = entry_pass.get()
        if usuario and nova_senha:
            conn = conectar()
            cursor = conn.cursor()
            senha_criptografada = hash_senha(nova_senha)
            cursor.execute("UPDATE usuarios SET senha = ? WHERE usuario = ?", (senha_criptografada, usuario))
            if cursor.rowcount:
                conn.commit()
                messagebox.showinfo("Sucesso", "Senha atualizada com sucesso.")
                janela.destroy()
            else:
                messagebox.showerror("Erro", "Usuário não encontrado.")
            conn.close()
        else:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")

    janela = tk.Toplevel(janela_pai)
    janela.title("Alterar Senha")
    janela.geometry("280x180")
    janela.resizable(False, False)

    tk.Label(janela, text="Usuário:").pack(pady=5)
    entry_user = tk.Entry(janela)
    entry_user.pack(pady=5)

    tk.Label(janela, text="Nova Senha:").pack(pady=5)
    entry_pass = tk.Entry(janela, show="*")
    entry_pass.pack(pady=5)

    tk.Button(janela, text="Atualizar", command=atualizar).pack(pady=10)

def excluir_usuario(janela_pai):
    def remover():
        usuario = entry_user.get()
        if usuario and usuario != "admin":
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE usuario = ?", (usuario,))
            if cursor.rowcount:
                conn.commit()
                messagebox.showinfo("Sucesso", "Usuário excluído com sucesso.")
                janela.destroy()
            else:
                messagebox.showerror("Erro", "Usuário não encontrado.")
            conn.close()
        else:
            messagebox.showwarning("Aviso", "Informe um usuário válido (não admin).")

    janela = tk.Toplevel(janela_pai)
    janela.title("Excluir Usuário")
    janela.geometry("280x140")
    janela.resizable(False, False)

    tk.Label(janela, text="Usuário a Excluir:").pack(pady=10)
    entry_user = tk.Entry(janela)
    entry_user.pack(pady=5)

    tk.Button(janela, text="Excluir", command=remover).pack(pady=10)

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
            WHERE data_retirada BETWEEN ? AND ?
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

def menu_admin():
        admin_win = tk.Tk()
        admin_win.title("Painel do Administrador")
        admin_win.geometry("320x410")
        admin_win.resizable(False, False)

        ttk.Label(admin_win, text="Bem-vindo, Admin!", font=("Segoe UI", 12, "bold")).pack(pady=10)

        criar_botao(admin_win, "Criar Novo Usuário", lambda: criar_novo_usuario(admin_win), COR_VERDE, "white").pack(pady=5)
        criar_botao(admin_win, "Alterar Senha de Usuário", lambda: alterar_senha(admin_win), COR_VERDE, "white").pack(pady=5)
        criar_botao(admin_win, "Excluir Usuário", lambda: excluir_usuario(admin_win), COR_VERDE, "white").pack(pady=5)
        criar_botao(admin_win, "Exportar para Excel", lambda: exportar_excel_por_periodo(admin_win), COR_VERDE, "white").pack(pady=5)
        criar_botao(admin_win, "Abrir Sistema", lambda: [admin_win.destroy(), iniciar_interface("admin")], COR_VERDE, "white").pack(pady=10)
        criar_botao(admin_win, "Registrar Devolução", lambda: [admin_win.destroy(), tela_devolucao(menu_admin)], COR_VERDE, "white").pack(pady=10)


        admin_win.mainloop()

def tela_login():
    inicializar_banco()

    def tentar_login():
        usuario = entry_usuario.get()
        senha = entry_senha.get()
        if validar_login(usuario, senha):
            login_win.destroy()
            if usuario == "admin":
                menu_admin()
            else:
                iniciar_interface(usuario)
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