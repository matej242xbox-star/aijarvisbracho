import subprocess
import os

vscode_path = os.path.join(os.getenv("LOCALAPPDATA"), "Programs", "Microsoft VS Code", "Code.exe")
if os.path.exists(vscode_path):
    subprocess.Popen(vscode_path)
else:
    subprocess.Popen("code", shell=True)
