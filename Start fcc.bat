@echo off
start powershell -NoExit -Command "fcc-server"
timeout /t 15 /nobreak 
start powershell -NoExit -Command "fcc-claude"