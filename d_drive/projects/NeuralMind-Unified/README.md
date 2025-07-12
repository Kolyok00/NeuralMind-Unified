# FusionAI Companion – Egyesített AI-ügynök, kódasszisztens és VTuber ökoszisztéma

**Fő üzenet:** A FusionAI Companion egy moduláris, teljesen ingyenes és self-hosted GitHub-projekt, amely ötvözi az OpenCode-ot, a Local Agentic Fusion blueprintet, a Desktop AI Companion & VTuber rendszert és Cole Medin legjobb AI-ügynök fejlesztési mintáit, hogy egy egységes AI-asszisztenst, kódgeneráló ügynököt és élő VTuber felületet kínáljon.

## 🚀 Projekt célja

A FusionAI Companion célja, hogy egyetlen, egységes monorepóban:

1. **Lokális és felhőalapú LLM-ekkel** kódot generáljon és önjavítson
2. **Dokumentum- és kódbázisokon** agentic RAG-ot és tudásgráfos lekérdezést végezzen
3. **Hangalapú interakciót**, VTuber élő streamet és webes UI-t biztosítson
4. **Folyamatos prompt tracinget**, hallucináció-detekciót és automatikus átirányítást valósítson meg
5. **Oktatóanyagokat és mintakódokat** tartalmazzon Cole Medin „ai-agents-masterclass" sorozatából

## 🏗️ Rendszerarchitektúra

| Modul | Funkció | Technológia |
|-------|---------|-------------|
| **FusionAI Core Agent** | Kódgenerálás, önjavítás, prompt-irányítás | OpenCode |
| **Ingest & Embed** | Web- és repo crawling, chunkolás, embedding | mcp-crawl4ai-rag + Supabase/pgvector |
| **Knowledge Graph** | Entitáskapcsolatok, GraphEval hallucináció-detekció | Neo4j + Graphiti + GraphEval NLI |
| **Agent Orchestrator** | Meta-ügynök létrehozása, Archon-típusú agentikus munkafolyamat | Archon + ai-agents-masterclass |
| **Workflow Automation** | Alacsony-kódú munkafolyamatok, automatikus javítás | n8n + ottomator-agents |
| **Chat & VTuber UI** | Webes chat-felület hanggal, VTuber avatar | Open WebUI + SnekStudio + Chatterbox TTS + Whisper.cpp |
| **Monitoring & Tracing** | Prompt- és token-statisztikák, hibadetektálás | Langfuse + custom dashboard |
| **CLI & TUI** | Teljes parancssori és TUI alapú interakció | OpenCode TUI + VS Code extension |

## � Gyors kezdés

### 1. Telepítés

**Windows PowerShell:**

```powershell
.\start.ps1
```

**Windows Command Prompt:**

```batch
start.bat
```

**Linux/Mac:**

```bash
chmod +x setup.sh
./setup.sh
```

### 2. Gyors demo futtatása

```bash
python quickstart.py
```

### 3. Teljes alkalmazás indítása

```bash
python main.py
```

### 4. Webes felület elérése

- **FusionAI API**: <http://localhost:8888>
- **Open WebUI (Chat)**: <http://localhost:3000>
- **n8n Workflows**: <http://localhost:5678>
- **Langfuse Monitoring**: <http://localhost:3001>
- **Neo4j Browser**: <http://localhost:7474>

## 🎯 Használati példák

### Kódgenerálás és önjavítás

```bash
opencode
# Prompt: "Írj egy Python függvényt, ami validál egy e-mail címet."
```

### Agentic RAG lekérdezés

1. Weboldal ingest n8n-flow-val → chunkolás embed-ek
2. Felhasználói kérdés: "Mi az új Pydantic V2 helyettesítőkezelése?"
3. Hybrid lekérdezés: Supabase vektorkeresés + Graphiti gráf-traversal
4. Válaszban releváns chunkok URL-ekkel és gráfútvonallal

### VTuber élő stream

1. SnekStudio VRM modell indítása
2. Hanginput Whisper.cpp → agentic prompt
3. Válasz Chatterbox TTS-sel → SnekStudio avatar mozgatása
4. OBS overlay Open WebUI chat üzenetekkel

## 🛠️ Segédeszközök és szkriptek

A projekt számos segédeszközt és szkriptet tartalmaz a könnyű használathoz:

### Telepítés és konfiguráció

- `setup_simple.py` - Egyszerű telepítési segédeszköz
- `install.py` - Részletes interaktív telepítő (fejlesztés alatt)

### Futtatás és indítás

- `start.bat` / `start.ps1` - Windows indító szkriptek
- `main.py` - Fő alkalmazás futtatása

### Demonstrációk és tesztelés

- `quickstart.py` - Gyors bemutató az alapfunkciókról
- `demo_simple.py` - Egyszerű demo szkript
- `demo_complete.py` - Teljes körű rendszerbemutató
- `health_check.py` - Rendszerállapot ellenőrzés
- `test_suite.py` - Automatikus tesztelési csomag

### Webes felület

- `static/index.html` - Modern webes felület
- `http://localhost:8888` - Fő webes interfész
- `http://localhost:8888/docs` - API dokumentáció

### Használati példák

```bash
# Gyors telepítés
python setup_simple.py

# Rendszer indítása
python main.py

# Gyors demo futtatása
python demo_simple.py

# Rendszerállapot ellenőrzése
python health_check.py

# Teljes tesztcsomag futtatása
python test_suite.py
```

## 🔧 Fejlesztés

A projekt moduláris felépítésű, minden komponens külön könyvtárban található:

- `core-agent/` - OpenCode AI kódgeneráló ügynök
- `ingest/` - Web crawling és embedding szolgáltatások
- `local-stack/` - Helyi AI infrastruktúra (Ollama, Supabase, stb.)
- `workflows/` - n8n automatizálási folyamatok
- `vtuber/` - VTuber avatar és streaming komponensek

## 📚 Dokumentáció

- [Telepítési útmutató részletesen](docs/installation.md)
- [Modulok dokumentációja](docs/modules/)
- [API referencia](docs/api/)
- [Példa munkafolyamatok](docs/examples/)

## 🤝 Közreműködés

Szívesen fogadjuk a közreműködéseket! Kérjük olvassa el a [CONTRIBUTING.md](CONTRIBUTING.md) fájlt a részletekért.

## 📄 Licenc

Ez a projekt MIT licenc alatt áll. Lásd a [LICENSE](LICENSE) fájlt a részletekért.

## 🙏 Köszönetnyilvánítás

- **Cole Medin** és csapata az AI-ügynök fejlesztési mintákért
- **OpenCode** közösség a terminál-alapú AI kódolásért
- **SnekStudio** a VTuber technológiáért
- Minden közreműködőnek és támogatónak

---

⚡ Powered by AI • 🚀 Built with Love • 🌟 Open Source Forever
