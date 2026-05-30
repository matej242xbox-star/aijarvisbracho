import subprocess
import os

spotify_path = os.path.join(os.getenv("APPDATA"), "Spotify", "Spotify.exe")
if os.path.exists(spotify_path):
    subprocess.Popen(spotify_path)
else:
    import webbrowser
    webbrowser.open("https://open.spotify.com")
