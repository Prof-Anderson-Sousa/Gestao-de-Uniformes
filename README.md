# 👕 Sistema de Gestão de Fardamentos

Este projeto foi desenvolvido em **Python + Tkinter + PostgreSQL** para auxiliar no controle de retirada e devolução de fardamentos por colaboradores.

## 🚀 Funcionalidades
- Login com senha criptografada (bcrypt)
- Painel administrativo
  - Criar, alterar e excluir usuários (com regras de senha forte e captcha para exclusão)
  - Gerenciar colaboradores (adicionar/remover)
  - Exportar registros em Excel
- Registro de retirada e devolução de fardas
- Controle por código de barras
- Interface simples e intuitiva

## 🛠 Tecnologias utilizadas
- **Python 3.11**
- **Tkinter** (interface gráfica)
- **PostgreSQL** (banco de dados)
- **psycopg2** (conector PostgreSQL)
- **bcrypt** (hash de senha)
- **python-dotenv** (variáveis de ambiente)
- **openpyxl** (exportação Excel)

## 📦 Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/gestao-de-fardamentos.git
   cd gestao-de-fardamentos