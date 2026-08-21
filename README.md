# 🏆 Copa São José 2026 - Sistema de Chaveamento & Mata-Mata

Aplicação web interativa para gerenciamento da **Copa São José 2026**. O sistema exibe os chaveamentos Masculino e Sub-12, a classificação e os jogos da categoria Feminino, calcula automaticamente o avanço entre as fases e persiste os placares em **SQLite**.

---

## 📌 Funcionalidades

- **Chaveamento Dinâmico:** Os vencedores avançam automaticamente para a próxima fase conforme os placares são definidos.
- **Gravação Automática (Auto-Save):** Ao digitar o placar, os dados são enviados e salvos diretamente no SQLite via API REST com técnica de *debounce* (300ms) para otimização de requisições.
- **Persistência de Dados:** Ao recarregar ou abrir a página em outro momento, todos os placares e o estado das chaves são restaurados do banco `torneio.db`.
- **Layout Responsivo:** 
  - Visualização completa da chave em computadores e tablets.
  - Abas navegáveis e botões de avanço rápido otimizados para smartphones.
- **Tema Visual:** Estilização escura moderna com paleta dourada e ciano inspirada em transmissões esportivas.
- **Autenticação:** Login, logout e cadastro de usuários com senha protegida por hash.
- **Controle de acesso:** Visitantes podem consultar placares; somente usuários autenticados podem editar resultados.
- **Auditoria:** Alterações de placares, logins, logouts e cadastros são registrados em logs.
- **Retenção de logs:** A aplicação mantém apenas os 20 eventos mais recentes, exibidos no fuso de Brasília.

---

## 🗂 Estrutura do Projeto

```text
copa-sao-jose/
├── app.py              # Servidor Flask, autenticação, API e SQLite
├── requirements.txt    # Dependências Python
├── torneio.db          # Banco SQLite gerado automaticamente
├── static/
│   ├── style.css       # Estilos da aplicação
│   └── logos/          # Escudos e logos dos times
└── templates/
    ├── index.html      # Chaveamentos, classificação e placares
    ├── login.html      # Tela de login
    ├── cadastrar.html  # Cadastro de usuários autenticados
    └── logs.html       # Histórico de auditoria
```

---

## 🛠 Tecnologias Utilizadas

- **Backend:** Python 3 + [Flask](https://flask.palletsprojects.com/)
- **Banco de Dados:** [SQLite3](https://www.sqlite.org/)
- **Frontend:** HTML5, CSS3 moderno (Flexbox, variáveis CSS, gradientes) e JavaScript nativo (Fetch API, DOM Events)
- **Tipografia:** Google Fonts (Montserrat)

---

## 🚀 Como Executar

### 1. Pré-requisitos
Certifique-se de ter o Python 3 instalado no sistema.

### 2. Criar e ativar um ambiente virtual (recomendado)

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Iniciar o servidor
Na pasta raiz do projeto, execute:

```bash
python app.py
```

### 5. Acessar a aplicação
Abra o navegador e acesse:
```text
http://localhost:5000
```
*(Para acessar de outros dispositivos na mesma rede local, use o IP da sua máquina seguido da porta `:5000`).*

### Usuário inicial

Na primeira execução, o banco cria automaticamente o usuário:

```text
Nome: admin
Senha: 123456
```

Para definir outro usuário inicial antes de criar o banco, configure `ADMIN_NAME` e `ADMIN_PASSWORD`.
Em produção, configure também uma chave forte em `FLASK_SECRET_KEY`.

---

## 🔌 Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Renderiza a página principal do torneio |
| `GET` | `/api/obter-placares` | Retorna todos os placares salvos no SQLite em formato JSON |
| `POST` | `/api/salvar-placar` | Salva/atualiza o placar; exige autenticação |
| `GET`/`POST` | `/login` | Autentica um usuário e registra o login |
| `POST` | `/logout` | Encerra a sessão e registra o logout |
| `GET`/`POST` | `/cadastrar` | Cadastra usuário autenticado com senha de 6 dígitos |
| `GET` | `/logs` | Exibe os 20 eventos mais recentes; exige autenticação |

## Banco de dados

O arquivo `torneio.db` é criado automaticamente com as tabelas:

- `partidas`: placares por identificador de partida.
- `usuarios`: nomes e hashes de senha.
- `logs`: usuário, ação e data/hora no fuso `America/Sao_Paulo`.

As credenciais são armazenadas com hash seguro. Não coloque o arquivo `torneio.db` ou a chave secreta em controle de versão público.

---

## 📄 Licença

Projeto desenvolvido para fins de controle e organização esportiva comunitária.
