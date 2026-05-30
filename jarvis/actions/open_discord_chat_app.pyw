import subprocess
import os

discord_path = os.path.join(os.getenv("LOCALAPPDATA"), "Discord", "Update.exe")
if os.path.exists(discord_path):
    subprocess.Popen([discord_path, "--processStart", "Discord.exe"])
else:
    import webbrowser
    webbrowser.open("https://discord.com/app")
