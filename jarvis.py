import requests
import pyttsx3
import json
import os
import webbrowser
import pywhatkit
import urllib.parse
import subprocess
from collections import Counter
import psutil  

# Sua chave da OpenAI
OPENAI_API_KEY = "SUA_CHAVE_AQUI"

## Memoria do Jarvis
ARQUIVO_MEMORIA = "memoria.json"

def carregar_memoria():
    if not os.path.exists(ARQUIVO_MEMORIA):
        return {}
    with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_memoria(dados):
    with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def salvar_pergunta(pergunta):
    memoria = carregar_memoria()
    memoria.setdefault("ultimas_perguntas", []).append(pergunta)
    memoria["ultimas_perguntas"] = memoria["ultimas_perguntas"][-10:]
    salvar_memoria(memoria)

def sugestao_baseada_em_habito():
    memoria = carregar_memoria()
    perguntas = memoria.get("ultimas_perguntas", [])
    if perguntas:
        contagem = Counter(perguntas)
        mais_comum = contagem.most_common(1)[0][0]
        return f"Deseja repetir: '{mais_comum}'?"
    return None

def falar(texto):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    voz_jarvis = next((voice.id for voice in voices if "Daniel" in voice.name), None)
    if voz_jarvis:
        engine.setProperty('voice', voz_jarvis)
    engine.setProperty('rate', 210)
    engine.setProperty('volume', 1.0)
    engine.say(texto)
    engine.runAndWait()
    engine.stop()

# Abrir e fechar apps
CAMINHOS_PERSONALIZADOS = {
    "spotify": "spotify",
    "vscode": "code",
    "chrome": "chrome",
    "bloco de notas": "notepad",
    "paint": "mspaint",
    "calculadora": "calc",
    "explorador": "explorer",
    "steam": r"C:\\Program Files (x86)\\Steam\\steam.exe"
}

EXECUTAVEIS_FECHAMENTO = {
    "spotify": "Spotify.exe",
    "vscode": "Code.exe",
    "chrome": "chrome.exe",
    "bloco de notas": "notepad.exe",
    "paint": "mspaint.exe",
    "calculadora": "calc.exe",
    "explorador": "explorer.exe",
    "steam": "steam.exe"
}

def abrir_app(app_nome):
    nome_normalizado = app_nome.lower().strip()
    comando = CAMINHOS_PERSONALIZADOS.get(nome_normalizado)
    if not comando:
        return f"Não conheço nenhum app chamado '{app_nome}'."
    try:
        subprocess.Popen(comando, shell=True)
        return f"Abrindo {nome_normalizado}."
    except Exception as e:
        return f"Não consegui abrir o app '{app_nome}'. Erro: {str(e)}"

def fechar_app(app_nome):
    nome_normalizado = app_nome.lower().strip()
    exe_nome = EXECUTAVEIS_FECHAMENTO.get(nome_normalizado)
    if not exe_nome:
        return f"Não sei como fechar o app '{app_nome}'."
    encontrado = False
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and proc.info['name'].lower() == exe_nome.lower():
            try:
                proc.kill()
                encontrado = True
            except Exception as e:
                return f"Erro ao tentar fechar o processo '{exe_nome}': {e}"
    if encontrado:
        return f"Fechando {nome_normalizado}."
    else:
        return f"Não encontrei nenhum processo chamado '{exe_nome}' para fechar."

def pesquisar_google(termo):
    query = urllib.parse.quote(termo)
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Pesquisando por '{termo}' no Google."

def tocar_musica(servico, musica):
    if servico == "youtube":
        pywhatkit.playonyt(musica)
        return f"Tocando {musica} no YouTube."
    elif servico == "spotify":
        os.system("start spotify")
        query = urllib.parse.quote(musica)
        url = f"https://open.spotify.com/search/{query}"
        webbrowser.open(url)
        return f"Procurando por '{musica}' no Spotify."
    else:
        return f"Serviço de música '{servico}' não reconhecido."

def pegar_clima(cidade):
    # OpenWeatherMap API
    chave = "SUA_CHAVE_OPENWEATHER_AQUI"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={chave}&units=metric&lang=pt_br"
    try:
        resposta = requests.get(url)
        dados = resposta.json()
        if dados.get("cod") == 200:
            descricao = dados["weather"][0]["description"]
            temperatura = dados["main"]["temp"]
            return f"Está {descricao} e fazendo {temperatura}°C em {cidade}."
        else:
            return "Não consegui obter o clima."
    except:
        return "Erro ao tentar obter dados do clima."

# ======= OpenAI Chat =======
def conversar_com_jarvis(pergunta):
    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": pergunta}],
        }
        resposta = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        resposta_json = resposta.json()
        return resposta_json['choices'][0]['message']['content']
    except Exception as e:
        return f"Erro ao acessar a IA: {str(e)}"

# ====== LOOP PRINCIPAL ======
def main():
    print("\n🤖 Jarvis 2.0 Iniciado. Digite 'sair' para encerrar.\n")
    falar("Jarvis ativado. Em que posso ajudar, senhor?")

    while True:
        pergunta = input("Você: ")
        if pergunta.lower() in ["sair", "exit", "quit"]:
            despedida = "Até mais, Guilherme. Sistema encerrado."
            print(f"Jarvis: {despedida}")
            falar(despedida)
            break

        salvar_pergunta(pergunta)

        # comandos diretos
        if "clima" in pergunta:
            cidade = "São Paulo"
            resposta = pegar_clima(cidade)
        elif "tocar" in pergunta:
            if "no spotify" in pergunta:
                musica = pergunta.replace("tocar", "").replace("no spotify", "").strip()
                resposta = tocar_musica("spotify", musica)
            else:
                musica = pergunta.replace("tocar", "").strip()
                resposta = tocar_musica("youtube", musica)
        elif "abrir" in pergunta:
            app = pergunta.replace("abrir", "").strip()
            resposta = abrir_app(app)
        elif "fechar" in pergunta:
            app = pergunta.replace("fechar", "").strip()
            resposta = fechar_app(app)
        elif "pesquisar" in pergunta:
            termo = pergunta.replace("pesquisar", "").strip()
            resposta = pesquisar_google(termo)
        else:
            resposta = conversar_com_jarvis(pergunta)

        print(f"Jarvis: {resposta}\n")
        falar(resposta)

        sugestao = sugestao_baseada_em_habito()
        if sugestao:
            print(f"Jarvis: {sugestao}")
            falar(sugestao)

if __name__ == "__main__":
    main()
