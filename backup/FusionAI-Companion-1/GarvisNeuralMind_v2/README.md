# GarvisNeuralMind 🚀

GarvisNeuralMind egy AI-alapú rendszer, amely modern nyelvi modellek és automatizációs eszközök integrálásával működik. 
Célja a mesterséges intelligencia asszisztensek teljes körű testreszabása és fejlesztése.

---

## **🔑 Főbb Funkciók**
✅ **Real-time voice interaction** – Hangalapú AI kommunikáció valós időben  
✅ **Automatikus modell finomhangolás (Fine-tuning)** – AI modellek adaptív tréningje  
✅ **Böngészővezérlés & AI-asszisztens integráció** – OpenRouter DeepSeek R1, Google AI Studio Gemini API, ChatGPT, Perplexity, Copilot támogatás  
✅ **VSCode Integráció** – Roo Code és UI-TARS támogatás  
✅ **Docker-alapú workflow** – Exolab Exo és n8n Gmail API integráció  
✅ **Többmodelles architektúra** – Ollama, vLLM, GPT4All, LlamaIndex, LangChain stb.  
✅ **Moduláris memória kezelés** – Pinecone, Redis, PostgreSQL, Neo4j stb.  

---

## **📌 Telepítés**
### **1. Klónozd a repót**
```sh
git clone https://github.com/felhasznalo/GarvisNeuralMind.git
cd GarvisNeuralMind
```

### **2. Függőségek telepítése**
#### 📌 **Python környezet**
```sh
pip install -r requirements.txt
```
#### 📌 **Docker alapú futtatás**
```sh
docker-compose up -d
```

---

## **🛠️ Használat**
### **1. Indítsd el az alkalmazást**
```sh
python main.py
```

### **2. API végpontok elérése**
A rendszer REST API és WebSocket felületet biztosít az interakciókhoz.

| Végpont | Leírás |
|---------|--------|
| `/api/chat` | AI beszélgetési interfész |
| `/api/memory` | Memória műveletek |
| `/api/fine-tune` | Modell finomhangolás |
| `/api/status` | Rendszerállapot |

---

## **📜 Dokumentáció**
A részletes dokumentáció a [docs](docs/) mappában található:

- [Telepítési útmutató](docs/installation.md)
- [Rendszer architektúra](docs/architecture.md)
- [Fine-tuning folyamat](docs/fine-tuning.md)
- [API Integrációk](docs/api-integration.md)
- [Roadmap](docs/roadmap.md)

---

## **🚀 Roadmap**
### **🟢 2025 Q1 (Jelenlegi Fejlesztések)**
- ✅ API stabilizálás (REST és WebSocket)
- ✅ AI asszisztens finomhangolás (NEAT alapú evolúciós algoritmusokkal)
- 🔄 Böngészővezérlés fejlesztése (Browser-Use + AI ügynökök)

### **🔵 2025 Q2**
- 🔄 LLM modellek GPU optimalizálása (Ollama, vLLM, GPT4All, stb.)
- 🔄 Automatikus pipeline CI/CD fejlesztés

---

## **📜 Licenc**
MIT License

**🎯 További információkért nézd meg a [dokumentációt](docs/)!**
