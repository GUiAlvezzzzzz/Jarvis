const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

// Função para adicionar mensagem
function adicionarMensagem(texto, remetente) {
  const div = document.createElement("div");
  div.className = "message " + remetente;
  div.textContent = texto;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Função falar
function falar(texto) {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(texto);
    utterance.lang = "pt-BR";
    speechSynthesis.speak(utterance);
  }
}

// Funções web
function tocarMusica(servico, musica) {
  if (servico === "youtube") {
    window.open(`https://www.youtube.com/results?search_query=${encodeURIComponent(musica)}`, "_blank");
    return `Tocando ${musica} no YouTube...`;
  } else if (servico === "spotify") {
    window.open(`https://open.spotify.com/search/${encodeURIComponent(musica)}`, "_blank");
    return `Procurando ${musica} no Spotify Web...`;
  }
}

// Pesquisa interna via DuckDuckGo Instant Answer API
async function pesquisarInterno(termo) {
  try {
    const response = await fetch(`https://api.duckduckgo.com/?q=${encodeURIComponent(termo)}&format=json&no_redirect=1&no_html=1&skip_disambig=1`);
    const data = await response.json();
    let resposta = data.Abstract || data.RelatedTopics?.[0]?.Text || "Desculpe, não encontrei nada sobre isso.";
    return resposta;
  } catch (err) {
    return "Erro ao pesquisar, tente novamente.";
  }
}

// Função animada "digitando"
async function digitarMensagem(texto) {
  const div = document.createElement("div");
  div.className = "message jarvis";
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;

  for (let i = 0; i <= texto.length; i++) {
    div.textContent = texto.substring(0, i);
    chatBox.scrollTop = chatBox.scrollHeight;
    await new Promise(r => setTimeout(r, 25)); // velocidade de digitação
  }

  falar(texto);
}

// Processa comandos do usuário
sendBtn.addEventListener("click", async () => {
  const pergunta = userInput.value.trim();
  if (!pergunta) return;
  adicionarMensagem(pergunta, "user");
  userInput.value = "";

  let resposta = "";

  if (pergunta.toLowerCase().includes("tocar")) {
    if (pergunta.toLowerCase().includes("spotify")) {
      const musica = pergunta.replace(/tocar/i, "").replace(/no spotify/i, "").trim();
      resposta = tocarMusica("spotify", musica);
      digitarMensagem(resposta);
    } else {
      const musica = pergunta.replace(/tocar/i, "").trim();
      resposta = tocarMusica("youtube", musica);
      digitarMensagem(resposta);
    }

  } else if (pergunta.toLowerCase().includes("pesquisar")) {
    const termo = pergunta.replace(/pesquisar/i, "").trim();
    digitarMensagem("Pesquisando...");
    const resultado = await pesquisarInterno(termo);
    digitarMensagem(resultado);

  } else if (pergunta.toLowerCase().includes("abrir spotify")) {
    resposta = "Abrindo Spotify Web...";
    window.open("https://open.spotify.com", "_blank");
    digitarMensagem(resposta);

  } else if (pergunta.toLowerCase().includes("abrir youtube")) {
    resposta = "Abrindo YouTube...";
    window.open("https://www.youtube.com", "_blank");
    digitarMensagem(resposta);

  } else {
    resposta = "Desculpe, ainda não sei isso. 😅";
    digitarMensagem(resposta);
  }
});

userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendBtn.click();
});

// Botões fixos
document.getElementById("btn-spotify").addEventListener("click", () => {
  adicionarMensagem("abrir spotify", "user");
  window.open("https://open.spotify.com", "_blank");
});

document.getElementById("btn-youtube").addEventListener("click", () => {
  adicionarMensagem("abrir youtube", "user");
  window.open("https://www.youtube.com", "_blank");
});

document.getElementById("btn-pesquisar").addEventListener("click", async () => {
  const termo = prompt("O que deseja pesquisar?");
  if (!termo) return;
  adicionarMensagem(`pesquisar ${termo}`, "user");
  digitarMensagem("Pesquisando...");
  const resultado = await pesquisarInterno(termo);
  digitarMensagem(resultado);
});
