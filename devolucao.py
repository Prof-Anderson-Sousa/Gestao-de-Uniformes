import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from banco import conectar
from sistema_fardamento import criar_botao
from sistema_fardamento import COR_VERDE, COR_AMARELO

COR_FUNDO = "#f2f2f2"
COR_TEXTO = "#333333"
COR_VERDE = "#5c7144"

def tela_devolucao(voltar_callback):
    janela = tk.Tk()
    janela.title("Devolução de Fardas")
    janela.geometry("720x480")
    janela.configure(bg=COR_FUNDO)

    # Estilo da Treeview
    style = ttk.Style(janela)
    style.theme_use("default")
    style.configure("Treeview",
                    background=COR_FUNDO,
                    foreground=COR_TEXTO,
                    rowheight=25,
                    fieldbackground=COR_FUNDO,
                    font=("Segoe UI", 9))
    style.configure("Treeview.Heading",
                    background=COR_VERDE,
                    foreground="white",
                    font=("Segoe UI", 10, "bold"))

    # Label e entrada de código
    tk.Label(janela, text="Código de Barras:", font=("Segoe UI", 10, "bold"), bg=COR_FUNDO).pack(pady=(10, 5))
    codigo_var = tk.StringVar()
    codigo_entry = ttk.Entry(janela, textvariable=codigo_var, width=30)
    codigo_entry.pack()
    codigo_entry.focus()

    # Frame da tabela com scrollbar
    frame_tabela = tk.Frame(janela, bg=COR_FUNDO)
    frame_tabela.pack(pady=20, fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_tabela)
    scrollbar.pack(side="right", fill="y")

    tree = ttk.Treeview(frame_tabela, yscrollcommand=scrollbar.set, columns=("nome", "tipo", "codigo", "retirada", "devolucao"), show="headings", height=10)
    tree.pack(fill="both", expand=True)
    scrollbar.config(command=tree.yview)

    tree.heading("nome", text="Nome")
    tree.heading("tipo", text="Tipo")
    tree.heading("codigo", text="Código")
    tree.heading("retirada", text="Retirada")
    tree.heading("devolucao", text="Devolução")

    tree.column("nome", width=180)
    tree.column("tipo", width=80)
    tree.column("codigo", width=100)
    tree.column("retirada", width=150)
    tree.column("devolucao", width=150)

    def atualizar_tabela():
        for row in tree.get_children():
            tree.delete(row)

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nome, tipo, codigo, data_retirada, hora_retirada, data_devolucao, hora_devolucao
            FROM registros
            ORDER BY id DESC
        """)
        for nome, tipo, codigo, data_ret, hora_ret, data_dev, hora_dev in cursor.fetchall():
            # Monta retirada no padrão brasileiro
            retirada = f"{datetime.strptime(data_ret, '%Y-%m-%d').strftime('%d/%m/%Y')} {hora_ret}"

            # Monta devolução, se houver
            if data_dev and hora_dev:
                devolucao = f"{datetime.strptime(data_dev, '%Y-%m-%d').strftime('%d/%m/%Y')} {hora_dev}"
            else:
                devolucao = "---"

            tree.insert("", "end", values=(nome, tipo, codigo, retirada, devolucao))
        conn.close()

    def registrar_devolucao_auto(*args):
        codigo = codigo_var.get().strip()
        if len(codigo) == 10:
            agora = datetime.now()
            data = agora.strftime("%Y-%m-%d")
            hora = agora.strftime("%H:%M:%S")

            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM registros WHERE codigo = ? AND data_devolucao IS NULL ORDER BY id DESC LIMIT 1", (codigo,))
            resultado = cursor.fetchone()
            if resultado:
                id_registro, nome = resultado
                cursor.execute("UPDATE registros SET data_devolucao = ?, hora_devolucao = ? WHERE id = ?", (data, hora, id_registro))
                conn.commit()
                messagebox.showinfo("Sucesso", f"Devolução registrada para {nome}.")
                atualizar_tabela()
            else:
                messagebox.showerror("Erro", "Nenhuma retirada pendente encontrada para este código.")

            conn.close()
            codigo_var.set("")

    # Atualiza quando digita 10 dígitos
    codigo_var.trace_add("write", registrar_devolucao_auto)

    # Botão voltar
    criar_botao(janela, "⬅ Voltar", lambda: [janela.destroy(), voltar_callback()], COR_AMARELO, "black").pack(pady=10)

    atualizar_tabela()
    janela.mainloop()
