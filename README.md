# 🤖 Chat com Gemini + Bot Telegram + Histórico local

Este projeto oferece um **chat web com IA Gemini** e um **bot do Telegram**, ambos com **memória de contexto local** e visual estilo terminal.

Tudo é instalado e configurado automaticamente pelo arquivo `setup_bot.py`.

---

## 📦 Funcionalidades

- 💬 **Chat Web com Gemini 1.5 Flash**
  - Interface estilo terminal
  - Histórico por sessão (armazenado localmente em `.json`)
  - Endpoint `/api/chat` com suporte a POST
  
- 🤖 **Bot Telegram com IA**
  - Usa as mesmas funções de contexto do web chat
  - Guarda o histórico por usuário do Telegram
  - Mensagens formatadas com clareza (sem confusão no contexto)

- 🗃️ **Histórico de conversas**
  - Página: `/log/<usuario_id>`
  - Lista de todos os históricos: `/log/all?senha=1234`
  - Armazenamento local em arquivos `historico_*.json`

---

## 🚀 Como usar

1. **Clone este repositório**

   ```bash
   git clone https://github.com/seu-usuario/chat-gemini-telegram
   cd chat-gemini-telegram
   ```

2. **Edite as chaves no `setup_bot.py`**

   Substitua:
   ```python
   GEMINI_API_KEY = "SUA_CHAVE_GEMINI"
   TELEGRAM_BOT_TOKEN = "SUA_CHAVE_TELEGRAM"
   ```

3. **Execute o setup**

   ```bash
   python setup_bot.py
   ```

4. **Rode o servidor**

   ```bash
   python main.py
   ```

---

## 🔒 Segurança

- O projeto usa **chaves diretamente no código**, ideal para testes locais.
- Para produção, mova para variáveis de ambiente ou `.env`.

---

## 📁 Estrutura

```
.
├── main.py                # Servidor Flask + Bot Telegram
├── storage.py             # Gerencia arquivos de histórico
├── templates/
│   ├── index.html         # Interface do chat
│   ├── log.html           # Histórico de um usuário
│   └── todos_logs.html    # Lista de todos os históricos
├── historico_*.json       # Arquivos locais gerados dinamicamente
├── requirements.txt
└── setup_bot.py           # Gera tudo automaticamente
```

---

## 📌 Tecnologias

- [Gemini 1.5 Flash API (Google)](https://ai.google.dev/)
- [Flask](https://flask.palletsprojects.com/)
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- HTML + estilo terminal com [Fira Code](https://fonts.google.com/specimen/Fira+Code)

---

## 💡 Inspiração

Este projeto foi inspirado na lógica de `startChat()` com `role: "user"` / `"model"`, exatamente como o SDK Gemini Web.

---

## ✨ Autor(a)

Feito com 💻 por [sonyddr6](https://github.com/sonyddr) — sinta-se livre para melhorar, forkear ou dar uma estrela ⭐
