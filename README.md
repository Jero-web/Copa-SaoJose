# 🏆 Copa São José 2026 - Sistema de Chaveamento & Mata-Mata

Aplicação web interativa para gerenciamento do chaveamento da **Copa São José 2026 (Mata-Mata)**. O sistema calcula automaticamente o avanço dos times entre as fases (Quartas de Final, Semifinais e Grande Final) e persiste os placares em tempo real em um banco de dados **SQLite**.

---

## 📌 Funcionalidades

- **Chaveamento Dinâmico:** Os vencedores avançam automaticamente para a próxima fase conforme os placares são definidos.
- **Gravação Automática (Auto-Save):** Ao digitar o placar, os dados são enviados e salvos diretamente no SQLite via API REST com técnica de *debounce* (300ms) para otimização de requisições.
- **Persistência de Dados:** Ao recarregar ou abrir a página em outro momento, todos os placares e o estado das chaves são restaurados do banco `torneio.db`.
- **Layout Responsivo:** 
  - Visualização completa da chave em computadores e tablets.
  - Abas navegáveis e botões de avanço rápido otimizados para smartphones.
- **Tema Visual:** Estilização escura moderna com paleta dourada e ciano inspirada em transmissões esportivas.

---

## 🗂 Estrutura do Projeto

```text
copa-sao-jose/
├── app.py              # Servidor Flask e rotas da API REST + SQLite
├── torneio.db          # Arquivo do banco de dados SQLite (gerado automaticamente)
└── templates/
    └── index.html      # Interface web completa (HTML, CSS e JS)
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

### 2. Instalar dependências
Instale o Flask usando o `pip`:

```bash
pip install flask
```

### 3. Iniciar o servidor
Na pasta raiz do projeto, execute:

```bash
python app.py
```

### 4. Acessar a aplicação
Abra o navegador e acesse:
```text
http://localhost:5000
```
*(Para acessar de outros dispositivos na mesma rede local, use o IP da sua máquina seguido da porta `:5000`).*

---

## 🔌 Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Renderiza a página principal do torneio |
| `GET` | `/api/obter-placares` | Retorna todos os placares salvos no SQLite em formato JSON |
| `POST` | `/api/salvar-placar` | Salva/atualiza o placar de uma partida (`match_id`, `score1`, `score2`) |

---

## 📄 Licença

Projeto desenvolvido para fins de controle e organização esportiva comunitária.
