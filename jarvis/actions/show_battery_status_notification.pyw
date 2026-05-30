import subprocess
import psutil

battery = psutil.sensors_battery()
if battery:
    percent = int(battery.percent)
    plugged = "Plugged in" if battery.power_plugged else "On battery"
    msg = f"Battery: {percent}% — {plugged}"
else:
    msg = "No battery info available."

subprocess.run([
    "powershell", "-command",
    f'[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms"); '
    f'$notify = New-Object System.Windows.Forms.NotifyIcon; '
    f'$notify.Icon = [System.Drawing.SystemIcons]::Information; '
    f'$notify.Visible = $true; '
    f'$notify.ShowBalloonTip(5000, "JARVIS — Battery", "{msg}", [System.Windows.Forms.ToolTipIcon]::Info);'
    f'Start-Sleep -Seconds 5; $notify.Dispose()'
], capture_output=True)
