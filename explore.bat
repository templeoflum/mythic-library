@echo off
title Mythic System Explorer
cd /d "%~dp0"
start http://localhost:8080
python scripts\serve_miroglyph.py
