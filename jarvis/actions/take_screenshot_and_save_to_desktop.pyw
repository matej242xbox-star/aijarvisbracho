import subprocess
import os
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
filename = os.path.join(desktop, f"screenshot_{timestamp}.png")

subprocess.run([
    "powershell",
    "-command",
    f'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::PrimaryScreen | Out-Null; $bmp = New-Object System.Drawing.Bitmap([System.Windows.Forms.SystemInformation]::VirtualScreen.Width, [System.Windows.Forms.SystemInformation]::VirtualScreen.Height); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen([System.Windows.Forms.SystemInformation]::VirtualScreen.Location, [System.Drawing.Point]::Empty, $bmp.Size); $bmp.Save("{filename}"); $g.Dispose(); $bmp.Dispose()'
], capture_output=True)
