# 💰 SaveMoney

Sistema web de **controle de finanças pessoais**, desenvolvido como projeto universitário.

## 📌 O que é o SaveMoney

O SaveMoney é uma aplicação web que permite que uma pessoa crie uma conta, faça login e controle suas **receitas**, **despesas**, **saldo** e **metas financeiras** de forma simples, visual e organizada.

## 🎯 Objetivo do projeto

Demonstrar, na prática, o desenvolvimento de uma aplicação web completa (frontend + backend + banco de dados) com autenticação de usuários, persistência de dados e visualização de informações financeiras através de dashboards e gráficos.

## 🛠️ Tecnologias utilizadas

**Frontend:** HTML5, CSS3, JavaScript (vanilla) e Chart.js (via CDN) para os gráficos.

**Backend:** Python com Flask, Flask-SQLAlchemy (ORM) e Flask-Login (autenticação/sessões).

**Banco de dados:** SQLite (arquivo local, criado automaticamente na primeira execução).

## ✅ Funcionalidades

- Cadastro de usuário com senha protegida por hash (Werkzeug)
- Login/logout com sessão de usuário (Flask-Login)
- Dashboard com saldo atual, receitas e despesas do mês, economia do mês
- Gráfico de receitas x despesas (últimos 6 meses)
- Gráfico de despesas por categoria (mês atual)
- Cadastro, edição e exclusão de receitas
- Cadastro, edição e exclusão de despesas
- Histórico de transações com filtros (tipo, período, categoria, busca por descrição)
- Gerenciamento de categorias personalizadas (categorias padrão criadas automaticamente)
- Metas financeiras com barra de progresso
- Planejamento mensal com limite de gastos e aviso de estouro
- Perfil do usuário (alterar nome e senha)
- Modo claro/escuro
- Layout responsivo (computador, tablet e celular)
- Mensagens de confirmação e de exclusão
- Dados de demonstração (via botão "Entrar com conta de demonstração" na tela de login)

## 📁 Estrutura do projeto

```text
SaveMoney/
│
├── app.py                # Ponto de entrada da aplicação (application factory)
├── config.py              # Configurações (chave secreta, caminho do banco)
├── extensions.py          # Instâncias do SQLAlchemy e do LoginManager
├── models.py               # Modelos: User, Category, Transaction, Goal, Planning
├── helpers.py              # Categorias padrão e geração de dados de demonstração
│
├── routes/                 # Blueprints (rotas) organizados por funcionalidade
│   ├── main.py              # Landing page
│   ├── auth.py               # Cadastro, login, logout
│   ├── dashboard.py          # Dashboard e dados dos gráficos
│   ├── transactions.py       # Receitas, despesas e histórico
│   ├── categories.py         # Gerenciamento de categorias
│   ├── goals.py               # Metas financeiras
│   ├── planning.py            # Planejamento mensal
│   └── profile.py             # Perfil do usuário
│
├── templates/               # Páginas HTML (Jinja2)
├── static/
│   ├── css/style.css         # Estilos (inclui tema claro/escuro e responsividade)
│   ├── js/main.js            # Tema, menu mobile, modal de confirmação
│   └── images/
│
├── database/                # Onde o arquivo savemoney.db é criado automaticamente
├── requirements.txt
└── README.md
```

## 💻 Como instalar e executar (VS Code ou terminal)

### 1. Pré-requisitos

- Python 3.10 ou superior instalado
- VS Code (opcional, mas recomendado)

### 2. Extrair o projeto

Extraia a pasta `SaveMoney` em um local de sua preferência e abra-a no VS Code (`Arquivo > Abrir Pasta...`).

### 3. Criar um ambiente virtual (recomendado)

Abra o terminal integrado do VS Code (`Terminal > Novo Terminal`) e execute:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5. Executar o projeto

```bash
python app.py
```

Na primeira execução, o banco de dados SQLite (`database/savemoney.db`) e todas as tabelas serão criados automaticamente — não é necessário nenhum comando extra de configuração.

### 6. Acessar o sistema

Abra o navegador em:

```
http://127.0.0.1:5000
```

## 🧪 Como testar

1. Clique em **"Criar conta"** na página inicial e cadastre um usuário, ou
2. Na tela de login, clique em **"Entrar com conta de demonstração"** para acessar automaticamente com dados fictícios já cadastrados (usuário `joao@teste.com`, senha `123456`), o que facilita a apresentação do projeto — o dashboard, os gráficos, uma meta e o planejamento já aparecerão preenchidos.
3. Após logar, use o menu lateral para navegar entre Dashboard, Receitas, Despesas, Transações, Categorias, Metas, Planejamento e Perfil.
4. Cadastre novas receitas/despesas e veja o Dashboard e os gráficos serem atualizados automaticamente.

## 🔒 Segurança implementada

- Senhas armazenadas com hash (nunca em texto puro), usando `werkzeug.security`
- Sessões de usuário via Flask-Login
- Todas as rotas internas protegidas com `@login_required`
- Cada usuário só acessa seus próprios dados (todas as consultas filtram por `user_id`)
- Validação de campos nos formulários (backend)
- `SECRET_KEY` configurável por variável de ambiente (`config.py`)

## ⚠️ Escopo do projeto

Este projeto foi desenvolvido para fins acadêmicos, com prazo curto de entrega. Por isso, **não foram implementados** recursos como Open Finance, integração bancária real, Pix, emissão de nota fiscal, IA avançada, multiempresa ou pagamentos reais — esses recursos poderão fazer parte de uma versão futura do SaveMoney.
