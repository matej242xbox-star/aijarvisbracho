# J.A.R.V.I.S — Your AI PC Controller

## Quick Start

1. **Install Python** (3.8+) if you haven't already: https://python.org

2. **Double-click `START_JARVIS.bat`**
   - It auto-installs required packages on first run
   - Starts the local server at http://localhost:5000

3. **Open your browser** and go to: http://localhost:5000

4. **Set your Gemini API key:**
   - Click **⚙ CONFIG** in the top right
   - Paste your Gemini API key (get one free at https://aistudio.google.com/app/apikey)
   - Click **SAVE & ENGAGE**

5. **Talk to JARVIS!**
   - Type commands like: "Open YouTube", "Mute volume", "Take a screenshot"
   - Gemini picks the best action and JARVIS executes it

---

## Adding New Actions

1. Create a new `.pyw` file inside the `actions/` folder
2. Name it **descriptively** — the name IS how Gemini understands what it does!
   - Good: `open_netflix_in_browser.pyw`
   - Good: `set_system_volume_to_max_100_percent.pyw`
   - Bad: `action1.pyw`
3. Write your Python code in the file
4. Restart JARVIS — it auto-discovers all `.pyw` files

---

## Folder Structure

```
jarvis/
│
├── START_JARVIS.bat        ← Double-click to start
├── jarvis_server.py        ← Backend (Flask + Gemini)
├── jarvis_ui.html          ← Web interface
├── requirements.txt        ← Python dependencies
├── config.json             ← Your API key (auto-created)
│
└── actions/                ← All your .pyw action files
    ├── open_google_in_browser.pyw
    ├── open_youtube_in_browser.pyw
    ├── mute_system_volume_audio.pyw
    └── ... (add more here!)
```

---

## Safety

- JARVIS **only** executes `.pyw` files inside the `actions/` folder
- No system damage possible — all actions are ones you create
- No internet required except for the Gemini API call

---

## Requirements (auto-installed by START_JARVIS.bat)

- flask, flask-cors
- requests
- psutil
- pycaw, comtypes (for volume control)
- winshell, pywin32 (for recycle bin)
