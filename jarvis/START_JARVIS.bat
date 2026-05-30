@echo off
title J.A.R.V.I.S
color 0A
echo.
echo  ============================================
echo    J.A.R.V.I.S  --  Starting up...
echo  ============================================
echo.
echo  [*] Open http://localhost:5000 in your browser
echo  [*] Press Ctrl+C here to shut down
echo.
python "%~dp0jarvis_server.py"
pause
