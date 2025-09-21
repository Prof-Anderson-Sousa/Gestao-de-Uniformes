import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk
from banco import conectar
import os

def carregar_colaboradores():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM colaboradores ORDER BY nome ASC")
    colaboradores = [row[0] for row in cursor.fetchall()]
    conn.close()
    return colaboradores

TIPOS = ["Camisa", "Calça"]
COR_FUNDO = "#f2f2f2"
COR_TEXTO = "#333333"
COR_VERDE = "#5c7144"
COR_AMARELO = "#f7d400"

def registrar_acao(acao, colaborador_var, tipo_var, codigo_entry):
    codigo = codigo_entry.get().strip()
    if not codigo:
        messagebox.showwarning("Atenção", "Informe o código.")
        return

    agora = datetime.now()
    data = agora.strftime("%Y-%m-%d")
    hora = agora.strftime("%H:%M:%S")

    conn = conectar()
    cursor = conn.cursor()

    if acao == "Retirada":
        nome = colaborador_var.get()
        tipo = tipo_var.get()
        if not nome or not tipo:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            conn.close()
            return

        cursor.execute("SELECT 1 FROM registros WHERE codigo = %s AND data_devolucao IS NULL", (codigo,))
        if cursor.fetchone():
            messagebox.showerror("Erro", "Essa farda já foi retirada e não foi devolvida.")
        else:
            cursor.execute("INSERT INTO registros (nome, tipo, codigo, data_retirada, hora_retirada) VALUES (%s, %s, %s, %s, %s)",
                           (nome, tipo, codigo, data, hora))
            conn.commit()
            messagebox.showinfo("Sucesso", "Retirada registrada.")

    elif acao == "Devolução":
        cursor.execute("SELECT id, nome FROM registros WHERE codigo = %s AND data_devolucao IS NULL ORDER BY id DESC LIMIT 1",
                       (codigo,))
        resultado = cursor.fetchone()
        if resultado:
            id_registro, nome = resultado
            cursor.execute("UPDATE registros SET data_devolucao = %s, hora_devolucao = %s WHERE id = %s",
                           (data, hora, id_registro))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Devolução registrada para {nome}.")
        else:
            messagebox.showerror("Erro", "Nenhuma retirada pendente encontrada para este código.")

    conn.close()
    codigo_entry.delete(0, tk.END)

def criar_botao(master, texto, comando, bg_color, fg_color, largura=200, altura=45):
    frame = tk.Frame(master, bg=COR_FUNDO)
    canvas = tk.Canvas(frame, width=largura, height=altura, bg=COR_FUNDO, highlightthickness=0)

    canvas.create_rectangle(2, 2, largura - 2, altura - 2, fill=bg_color, outline=bg_color)
    canvas.create_text(largura // 2, altura // 2, text=texto, fill=fg_color, font=("Segoe UI", 10, "bold"))

    canvas.config(cursor="hand2")
    canvas.bind("<Button-1>", lambda e: comando())
    canvas.pack()
    return frame


def filtrar_colaboradores(combo, var):
    texto = var.get().lower()
    opcoes_filtradas = [nome for nome in carregar_colaboradores() if nome.lower().startswith(texto)]
    combo['values'] = opcoes_filtradas
    if opcoes_filtradas:
        combo.event_generate('<Down>')

def voltar_para_menu(janela_atual, usuario_logado):
    janela_atual.destroy()
    if usuario_logado == "admin":
        from login import menu_admin
        menu_admin(usuario_logado)
    else:
        from login import menu_usuario
        menu_usuario(usuario_logado)

      

def iniciar_interface(usuario_logado):
    janela = tk.Tk()
    janela.title("Controle de Fardamentos")
    janela.geometry("520x340")
    janela.resizable(False, False)
    janela.configure(bg=COR_FUNDO)

    frame = tk.Frame(janela, bg=COR_FUNDO)
    frame.pack(pady=10)
    frame.grid_columnconfigure(0, minsize=120)

    btn_voltar = criar_botao(janela, "⬅ Voltar", lambda: voltar_para_menu(janela, usuario_logado), COR_AMARELO, "black", largura=110, altura=35)
    btn_voltar.place(x=10, y=10)

    tk.Label(frame, text="Colaborador:", font=("Segoe UI", 10, "bold"), bg=COR_FUNDO).grid(row=0, column=0, sticky="w", padx=5, pady=5)
    colaborador_var = tk.StringVar()
    colaborador_combo = ttk.Combobox(frame, textvariable=colaborador_var, values=carregar_colaboradores(), width=30)
    colaborador_combo.grid(row=0, column=1, padx=5, pady=5)
    colaborador_combo.bind("<KeyRelease>", lambda e: filtrar_colaboradores(colaborador_combo, colaborador_var))

    tk.Label(frame, text="Tipo de Farda:", font=("Segoe UI", 10, "bold"), bg=COR_FUNDO).grid(row=1, column=0, sticky="w", padx=5, pady=5)
    tipo_var = tk.StringVar()
    tipo_combo = ttk.Combobox(frame, textvariable=tipo_var, values=TIPOS, width=30)
    tipo_combo.grid(row=1, column=1, padx=5, pady=5)
    tipo_combo.current(0)

    tk.Label(frame, text="Código de Barras:", font=("Segoe UI", 10, "bold"), bg=COR_FUNDO).grid(row=2, column=0, sticky="w", padx=5, pady=5)
    codigo_entry = ttk.Entry(frame, width=33)
    codigo_entry.grid(row=2, column=1, padx=5, pady=10, ipady=5)

    botoes_frame = tk.Frame(janela, bg=COR_FUNDO)
    botoes_frame.pack(pady=30)

    criar_botao(botoes_frame, "\ud83d\udce6 Retirar", lambda: registrar_acao("Retirada", colaborador_var, tipo_var, codigo_entry), COR_VERDE, "white").pack(side="left", padx=20)

    janela.mainloop()