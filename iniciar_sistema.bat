@echo off
title Sistema Comparador de Perfumes - Miami a Peru
echo =======================================================
echo   SISTEMA DE ARBITRAJE Y COMPARACION DE PERFUMES
echo   Crist Fragrances vs Perfumes Wholesale USA
echo =======================================================
echo.
echo Iniciando servidor local en http://localhost:8000 ...
start "" http://localhost:8000
python -m uvicorn server:app --host 127.0.0.1 --port 8000
pause
