"""
JARVIS - Zero-dependency backend
Uses only Python standard library. No pip install needed.
"""

import http.server
import json
import os
import subprocess
import glob
import webbrowser
import urllib.request
import urllib.error
from datetime import datetime

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ACTIONS_DIR = os.path.join(BASE_DIR, "actions")
CONFIG_FILE   = os.path.join(BASE_DIR, "config.json")
MAP_LOC_FILE  = os.path.join(BASE_DIR, "last_location.json")
WEATHER_FILE  = os.path.join(BASE_DIR, "last_weather.json")
GEMINI_URL    = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

# ── Config ────────────────────────────────────────────────────────────────────
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"api_key": ""}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

# ── Actions ───────────────────────────────────────────────────────────────────
def get_actions():
    files = glob.glob(os.path.join(ACTIONS_DIR, "*.pyw"))
    return sorted([os.path.splitext(os.path.basename(f))[0] for f in files])

def execute_action(name):
    filepath = os.path.join(ACTIONS_DIR, f"{name}.pyw")
    real_actions = os.path.realpath(ACTIONS_DIR)
    real_file    = os.path.realpath(filepath)
    if not real_file.startswith(real_actions):
        return False, "Security: file outside actions folder."
    if not os.path.exists(filepath):
        return False, f"Not found: {name}.pyw"
    try:
        subprocess.Popen(["pythonw", filepath], cwd=ACTIONS_DIR)
        return True, f"Executed: {name}"
    except Exception as e:
        return False, str(e)

# ── Gemini ────────────────────────────────────────────────────────────────────
def ask_gemini(user_message, api_key, history):
    actions = get_actions()
    actions_list = "\n".join(f"- {a}" for a in actions)
    system_prompt = f"""You are JARVIS, an AI assistant controlling a Windows PC via Python action files.

AVAILABLE ACTIONS (exact filenames without .pyw):
{actions_list}

RULES:
1. ALWAYS reply with a JSON array — even for a single task. Never return a plain object.
2. Each item in the array is one task. For normal actions:
   {{"action":"exact_name","execute":true}}
3. If the user asks for MULTIPLE things, include ALL of them as separate items in the array.
   Example — "open YouTube and mute the volume":
   [{{"action":"open_youtube_in_browser","execute":true}},{{"action":"mute_system_volume_audio","execute":true}}]
4. The LAST item (or only item) must include a "message" field with your witty JARVIS reply summarising everything you did.
5. If nothing matches or user is just chatting:
   [{{"action":null,"execute":false,"message":"your reply here"}}]
6. SPECIAL DYNAMIC ACTIONS — include the extra field when needed:
   MAP:     {{"action":"open_jarvis_map_and_locate_place","execute":true,"location":"New York"}}
   VOLUME:  {{"action":"set_system_volume_to_any_percent","execute":true,"volume":70}}
   GOOGLE:  {{"action":"search_google_for_any_query","execute":true,"query":"best pizza"}}
   YOUTUBE SEARCH: {{"action":"search_youtube_for_any_query","execute":true,"query":"lo fi music"}}
   WEATHER: {{"action":"open_weather_for_any_city","execute":true,"city":"London"}}
7. Be concise and witty like JARVIS from Iron Man.
8. NEVER invent action names. Only use names from the list or the special actions above.
9. Reply ONLY with the JSON array. No markdown, no backticks, no explanation outside the JSON.

Current time: {datetime.now().strftime("%A %B %d %Y %I:%M %p")}"""

    messages = []
    for h in history[-10:]:
        messages.append({"role": h["role"], "parts": [{"text": h["content"]}]})
    messages.append({"role": "user", "parts": [{"text": user_message}]})

    payload = json.dumps({
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": messages,
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024}
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{GEMINI_URL}?key={api_key}",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Strip accidental code fences
    if "```" in text:
        for p in text.split("```"):
            p = p.strip()
            if p.startswith("json"): p = p[4:].strip()
            if p.startswith("[") or p.startswith("{"):
                text = p; break

    parsed = json.loads(text)
    # Normalise: always return a list
    if isinstance(parsed, dict):
        parsed = [parsed]
    return parsed

# ── Request handler ───────────────────────────────────────────────────────────
class JarvisHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # silence request logs

    def send_json(self, code, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, path):
        try:
            with open(path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_html(os.path.join(BASE_DIR, "jarvis_ui.html"))
        elif self.path in ("/map", "/map.html"):
            self.send_html(os.path.join(BASE_DIR, "jarvis_map.html"))
        elif self.path in ("/weather", "/weather.html"):
            self.send_html(os.path.join(BASE_DIR, "jarvis_weather.html"))
        elif self.path == "/api/actions":
            self.send_json(200, {"actions": get_actions()})
        elif self.path == "/api/config":
            cfg = load_config()
            self.send_json(200, {"has_key": bool(cfg.get("api_key"))})
        elif self.path == "/api/map-location":
            if os.path.exists(MAP_LOC_FILE):
                with open(MAP_LOC_FILE) as f:
                    data = json.load(f)
                self.send_json(200, data)
            else:
                self.send_json(200, {"location": ""})
        elif self.path == "/api/weather-city":
            if os.path.exists(WEATHER_FILE):
                with open(WEATHER_FILE) as f:
                    data = json.load(f)
                self.send_json(200, data)
            else:
                self.send_json(200, {"city": ""})
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        length  = int(self.headers.get("Content-Length", 0))
        raw     = self.rfile.read(length)
        try:
            body = json.loads(raw.decode("utf-8")) if raw else {}
        except Exception:
            body = {}

        if self.path == "/api/config":
            cfg = load_config()
            cfg["api_key"] = body.get("api_key", "")
            save_config(cfg)
            self.send_json(200, {"ok": True})

        elif self.path == "/api/clear-location":
            if os.path.exists(MAP_LOC_FILE):
                os.remove(MAP_LOC_FILE)
            self.send_json(200, {"ok": True})

        elif self.path == "/api/clear-weather":
            if os.path.exists(WEATHER_FILE):
                os.remove(WEATHER_FILE)
            self.send_json(200, {"ok": True})

        elif self.path == "/api/execute":
            action_name = body.get("action", "")
            if action_name == "open_jarvis_map_and_locate_place":
                # No location provided from sidebar — just open the map
                if os.path.exists(MAP_LOC_FILE):
                    os.remove(MAP_LOC_FILE)
                webbrowser.open("http://localhost:5000/map")
                self.send_json(200, {"ok": True, "message": "Map opened"})
            else:
                ok, msg = execute_action(action_name)
                self.send_json(200, {"ok": ok, "message": msg})

        elif self.path == "/api/chat":
            msg     = body.get("message", "").strip()
            history = body.get("history", [])
            if not msg:
                self.send_json(400, {"error": "Empty message"}); return
            cfg = load_config()
            api_key = cfg.get("api_key", "")
            if not api_key:
                self.send_json(400, {"error": "No API key. Click ⚙ CONFIG to add your Gemini key."}); return
            try:
                tasks = ask_gemini(msg, api_key, history)
            except Exception as e:
                self.send_json(500, {"error": f"Gemini error: {e}"}); return

            # Extract the reply message (last task that has one, or first)
            reply_msg = ""
            for t in reversed(tasks):
                if t.get("message"):
                    reply_msg = t["message"]; break
            if not reply_msg:
                reply_msg = "Done, sir."

            # Execute every task
            results = []
            for task in tasks:
                action_name = task.get("action")
                if not task.get("execute") or not action_name:
                    continue
                executed = False; exec_error = None

                if action_name == "open_jarvis_map_and_locate_place":
                    location = task.get("location", "")
                    with open(MAP_LOC_FILE, "w") as f:
                        json.dump({"location": location}, f)
                    webbrowser.open("http://localhost:5000/map")
                    executed = True

                elif action_name == "set_system_volume_to_any_percent":
                    vol = max(0, min(100, int(task.get("volume", 50))))
                    ps_clean = f"""
Add-Type -TypeDefinition @'
using System.Runtime.InteropServices;
using System;
[Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioEndpointVolume {{
    int _VtblGap1_6();
    int SetMasterVolumeLevelScalar(float fLevel, Guid pguidEventContext);
}}
[Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDevice {{
    int Activate([MarshalAs(UnmanagedType.LPStruct)] Guid iid, int dwClsCtx, IntPtr pActivationParams, [MarshalAs(UnmanagedType.IUnknown)] out object ppInterface);
    int f(); int g();
}}
[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDeviceEnumerator {{
    int f();
    int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice ppEndpoint);
}}
[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
class MMDeviceEnumeratorComObject {{}}
public class Vol {{
    public static void Set(float v) {{
        var enumerator = (IMMDeviceEnumerator)new MMDeviceEnumeratorComObject();
        IMMDevice dev; enumerator.GetDefaultAudioEndpoint(0, 1, out dev);
        object o; dev.Activate(typeof(IAudioEndpointVolume).GUID, 23, IntPtr.Zero, out o);
        ((IAudioEndpointVolume)o).SetMasterVolumeLevelScalar(v, Guid.Empty);
    }}
}}
'@
[Vol]::Set({vol}/100.0)
"""
                    subprocess.run(["powershell", "-NoProfile", "-Command", ps_clean],
                                   capture_output=True, timeout=10)
                    executed = True

                elif action_name == "search_google_for_any_query":
                    import urllib.parse
                    query = task.get("query", "")
                    webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}")
                    executed = True

                elif action_name == "search_youtube_for_any_query":
                    import urllib.parse
                    query = task.get("query", "")
                    webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}")
                    executed = True

                elif action_name == "open_weather_for_any_city":
                    city = task.get("city", "")
                    with open(WEATHER_FILE, "w") as f:
                        json.dump({"city": city}, f)
                    webbrowser.open("http://localhost:5000/weather")
                    executed = True

                else:
                    ok, emsg = execute_action(action_name)
                    executed = ok
                    if not ok: exec_error = emsg

                results.append({
                    "action":   action_name,
                    "executed": executed,
                    "error":    exec_error
                })

            self.send_json(200, {
                "message": reply_msg,
                "results": results,
                # legacy single-action fields for UI compatibility
                "action":     results[0]["action"]   if results else None,
                "executed":   results[0]["executed"] if results else False,
                "exec_error": results[0]["error"]    if results else None,
            })
        else:
            self.send_response(404); self.end_headers()

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    PORT = 5000
    server = http.server.HTTPServer(("127.0.0.1", PORT), JarvisHandler)
    print("=" * 48)
    print("  J.A.R.V.I.S is online.")
    print(f"  Open http://localhost:{PORT} in your browser.")
    print("  Press Ctrl+C to shut down.")
    print("=" * 48)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  JARVIS offline.")
