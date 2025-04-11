import os
import subprocess
import sys

# Arquivo: main.py
main_py = """
import os
import time
import uuid
import threading
import webbrowser
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, session
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from threading import Lock
from storage import carregar_historico, salvar_historico, listar_arquivos

flask_app = Flask(__name__)
flask_app.secret_key = os.environ.get("SECRET_KEY", str(uuid.uuid4()))

GEMINI_API_KEY = "AIzaSyDF5wOFJPEuhrlD9s0m1ZjYLg-IIPWsCRg"
TELEGRAM_BOT_TOKEN = "7730224947:AAG5ENF-HVlD33CbJib0NK2GNXL3E7UYzcw"


genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

chat_log_lock = Lock()

def gerar_resposta_com_contexto(historico, pergunta):
    history = []
    for _, p, r in historico[-500:]:
        history.append({ "role": "user", "parts": [ { "text": p } ] })
        history.append({ "role": "model", "parts": [ { "text": r } ] })
    history.append({ "role": "user", "parts": [ { "text": pergunta } ] })
    response = model.generate_content(history)
    return response.text

# TELEGRAM
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pergunta = update.message.text
    nome = update.message.from_user.first_name or "Usuário"
    user_id = "telegram_" + str(update.message.from_user.id)
    try:
        historico = carregar_historico(user_id)
        resposta = gerar_resposta_com_contexto(historico, pergunta)
        await update.message.reply_text(resposta)
        with chat_log_lock:
            historico.append((nome, pergunta, resposta))
            salvar_historico(historico, user_id)
    except Exception as e:
        await update.message.reply_text(f"Erro: {str(e)}")

# FLASK (Web)
@flask_app.route("/")
def index():
    if "sess_id" not in session:
        session["sess_id"] = "web_" + str(uuid.uuid4())
    return render_template("index.html", sess_id=session["sess_id"])

@flask_app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    pergunta = data.get("mensagem", "")
    sess_id = session.get("sess_id", "anon")
    try:
        historico = carregar_historico(sess_id)
        resposta = gerar_resposta_com_contexto(historico, pergunta)
        with chat_log_lock:
            historico.append(("WebUser", pergunta, resposta))
            salvar_historico(historico, sess_id)
    except Exception as e:
        resposta = f"Erro ao gerar resposta: {str(e)}"
    return jsonify({"resposta": resposta})

@flask_app.route("/log/<usuario_id>")
def log_usuario(usuario_id):
    historico = carregar_historico(usuario_id)
    return render_template("log.html", log=historico, usuario_id=usuario_id)

@flask_app.route("/log/all")
def log_all():
    senha = request.args.get("senha")
    if senha != "1234":
        return "Acesso negado.", 403
    arquivos = listar_arquivos()
    return render_template("todos_logs.html", arquivos=arquivos)

def iniciar_flask():
    webbrowser.open("http://127.0.0.1:5000")
    flask_app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    threading.Thread(target=iniciar_flask).start()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.run_polling()

"""

# Arquivo: storage.py
storage_py = """
import json
import os
import glob

def get_arquivo(usuario_id):
    return f"historico_{usuario_id}.json"

def carregar_historico(usuario_id="geral"):
    arquivo = get_arquivo(usuario_id)
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_historico(historico, usuario_id="geral"):
    arquivo = get_arquivo(usuario_id)
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

def listar_arquivos():
    arquivos = glob.glob("historico_*.json")
    return [arq.replace("historico_", "").replace(".json", "") for arq in arquivos]
"""

# HTML: index.html
index_html = '''<!DOCTYPE html>
<html lang="pt-br"><head><meta charset="UTF-8"><title>Chat com Gemini</title><link href="https://fonts.googleapis.com/css2?family=Fira+Code&display=swap" rel="stylesheet">
<style>
body { margin: 0; background: #121212; color: #eee; font-family: 'Fira Code', monospace; display: flex; justify-content: center; align-items: flex-start; padding: 2rem; height: 100vh; }
.chat-container { background-color: #1e1e1e; border: 1px solid #333; padding: 1rem; border-radius: 5px; width: 90%; max-width: 800px; height: 90vh; display: flex; flex-direction: column; }
#mensagens { flex: 1; overflow-y: auto; white-space: pre-wrap; }
.linha-input { display: flex; align-items: center; margin-top: 1rem; }
.prompt { color: #00ff00; margin-right: 0.5rem; }
input { flex: 1; background: none; border: none; color: #fff; font-family: inherit; font-size: 1rem; outline: none; }
.user { color: #9cdcfe; } .bot  { color: #ce9178; }
</style></head><body>
<div class="chat-container"><div id="mensagens">> Olá! Pronto para conversar com o Gemini.\n</div>
<div class="linha-input"><span class="prompt">$</span><input type="text" id="entrada" placeholder="Digite sua mensagem..."></div>
<div style="text-align:center; margin-top: 1rem;"><a href="/log/{{ sess_id }}" style="color:#00ff00; font-size:0.9rem; text-decoration:none;">Ver histórico da sessão</a></div></div>
<script>
const entrada = document.getElementById("entrada");
const mensagens = document.getElementById("mensagens");
async function enviar() {
  const pergunta = entrada.value.trim();
  if (!pergunta) return;
  mensagens.innerHTML += `<div class="user">$ ${pergunta}</div>`;
  entrada.value = ""; entrada.disabled = true;
  const resp = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mensagem: pergunta })
  });
  const json = await resp.json();
  mensagens.innerHTML += `<div class="bot">🤖 Gemini > ${json.resposta}</div>`;
  mensagens.scrollTop = mensagens.scrollHeight;
  entrada.disabled = false; entrada.focus();
}
entrada.addEventListener("keydown", (e) => { if (e.key === "Enter") enviar(); });
</script></body></html>'''

# HTMLs adicionais
log_html = '''<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><title>Histórico - Gemini</title>
<link href="https://fonts.googleapis.com/css2?family=Fira+Code&display=swap" rel="stylesheet">
<style>
body { background: #121212; color: #eee; font-family: 'Fira Code', monospace; padding: 2rem; }
h1 { text-align: center; color: #00ff00; }
.terminal { background: #1e1e1e; border: 1px solid #333; border-radius: 5px; padding: 1rem; max-width: 900px; margin: auto; }
.linha { margin-bottom: 1rem; }
.user { color: #9cdcfe; }
.bot { color: #ce9178; }
</style></head><body><h1>📜 Histórico de {{ usuario_id }}</h1>
<div class="terminal">
{% if log and log|length > 0 %}
  {% for nome, pergunta, resposta in log %}
    <div class="linha"><span class="user">$ {{ nome }}: {{ pergunta }}</span></div>
    <div class="linha"><span class="bot">🤖 Gemini > {{ resposta }}</span></div>
    <hr style="border-color:#333">
  {% endfor %}
{% else %}
  <div class="linha">> Nenhuma mensagem encontrada para este usuário.</div>
{% endif %}
</div>
<div style="text-align:center; margin-top: 1rem;">
  <a href="/" style="color:#00ff00; text-decoration:none;">⬅️ Voltar ao chat</a>
</div>
</body></html>'''

todos_logs_html = '''<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><title>Todos os Históricos</title>
<link href="https://fonts.googleapis.com/css2?family=Fira+Code&display=swap" rel="stylesheet">
<style>
body { background: #121212; color: #eee; font-family: 'Fira Code', monospace; padding: 2rem; }
h1 { text-align: center; color: #00ff00; }
.lista { max-width: 900px; margin: auto; }
a { display: block; margin: 0.5rem 0; color: #4caf50; text-decoration: none; }
</style></head><body><h1>📂 Todos os Históricos</h1>
<div class="lista">
  {% for user_id in arquivos %}
    <a href="/log/{{ user_id }}">/log/{{ user_id }}</a>
  {% endfor %}
</div>
<div style="text-align:center; margin-top: 1rem;">
  <a href="/" style="color:#00ff00; text-decoration:none;">⬅️ Voltar ao chat</a>
</div>
</body></html>'''

requirements_txt = '''
python-telegram-bot==20.7
google-generativeai==0.4.1
Flask==3.0.2
'''

# Criação dos arquivos
os.makedirs("templates", exist_ok=True)
with open("main.py", "w", encoding="utf-8") as f: f.write(main_py.strip())
with open("storage.py", "w", encoding="utf-8") as f: f.write(storage_py.strip())
with open("templates/index.html", "w", encoding="utf-8") as f: f.write(index_html.strip())
with open("templates/log.html", "w", encoding="utf-8") as f: f.write(log_html.strip())
with open("templates/todos_logs.html", "w", encoding="utf-8") as f: f.write(todos_logs_html.strip())
with open("requirements.txt", "w", encoding="utf-8") as f: f.write(requirements_txt.strip())

# Instalação
print("📦 Instalando dependências...")
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
print("✅ Projeto criado! Execute com: python main.py")
