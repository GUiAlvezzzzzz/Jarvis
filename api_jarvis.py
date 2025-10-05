from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import psutil
import urllib.parse
import webbrowser

app = Flask(__name__)
CORS(app)  # permite comunicação com o frontend

# ===== Comandos que o Jarvis conhece =====
CAMINHOS_PERSONALIZADOS = {
    "spotify": "spotify",
    "vscode": "code",
    "chrome": "chrome",
    "bloco de notas": "notepad",
    "paint": "mspaint",
    "calculadora": "calc",
    "explorador": "explorer"
}

EXECUTAVEIS_FECHAMENTO = {
    "spotify": "Spotify.exe",
    "vscode": "Code.exe",
    "chrome": "chrome.exe",
    "bloco de notas": "notepad.exe",
    "paint": "mspaint.exe",
    "calculadora": "calc.exe",
    "explorador": "explorer.exe"
}

# ===== Funções =====
def abrir_app(app_nome):
    comando = CAMINHOS_PERSONALIZADOS.get(app_nome.lower())
    if not comando:
        return f"Não conheço app '{app_nome}'."
    try:
        subprocess.Popen(comando, shell=True)
        return f"Abrindo {app_nome}."
    except Exception as e:
        return f"Erro ao abrir {app_nome}: {e}"

def fechar_app(app_nome):
    exe_nome = EXECUTAVEIS_FECHAMENTO.get(app_nome.lower())
    if not exe_nome:
        return f"Não sei como fechar '{app_nome}'."
    encontrado = False
    for proc in psutil.process_iter(['pid','name']):
        if proc.info['name'] and proc.info['name'].lower() == exe_nome.lower():
            proc.kill()
            encontrado = True
    return f"Fechando {app_nome}." if encontrado else f"'{app_nome}' não está aberto."

def tocar_musica(musica):
    webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote(musica)}")
    return f"Tocando '{musica}' no YouTube."

# ===== Endpoint principal =====
@app.route("/api/execute", methods=["POST"])
def execute():
    data = request.get_json()
    pergunta = data.get("pergunta","").lower()

    if "abrir " in pergunta:
        app_nome = pergunta.replace("abrir ","").strip()
        resposta = abrir_app(app_nome)
    elif "fechar " in pergunta:
        app_nome = pergunta.replace("fechar ","").strip()
        resposta = fechar_app(app_nome)
    elif "tocar " in pergunta:
        musica = pergunta.replace("tocar ","").strip()
        resposta = tocar_musica(musica)
    elif "diagnostico" in pergunta:
        resposta = f"CPU: {psutil.cpu_percent()}%, Memória: {psutil.virtual_memory().percent}%, Disco: {psutil.disk_usage('/').percent}%"
    else:
        resposta = f"Não sei como responder '{pergunta}' ainda."

    return jsonify({"resposta": resposta})

# ===== Rodar o servidor =====
if __name__ == "__main__":
    app.run(port=5000)
