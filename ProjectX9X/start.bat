@echo off
echo.
echo 🚀 Iniciando AutomationX9X...
echo =============================
echo.

REM Verificar se os diretórios existem
if not exist "backend" (
    echo ❌ Diretório backend não encontrado!
    echo Execute este script do diretório raiz do projeto.
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ Diretório frontend não encontrado!
    echo Execute este script do diretório raiz do projeto.
    pause
    exit /b 1
)

REM Verificar se as dependências estão instaladas
if not exist "backend\venv" (
    echo ❌ Ambiente virtual Python não encontrado!
    echo Execute primeiro: scripts\install.bat
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo ❌ Módulos Node.js não encontrados!
    echo Execute primeiro: scripts\install.bat
    pause
    exit /b 1
)

REM Criar arquivo para controlar processos
echo. > .processes

REM Iniciar backend
echo 🐍 Iniciando backend Python...
cd backend
call venv\Scripts\activate.bat
start "AutomationX9X Backend" /min cmd /c "uvicorn main:app --reload --host 0.0.0.0 --port 8000 && pause"

REM Aguardar backend inicializar
timeout /t 5 /nobreak >nul

echo ✅ Backend iniciado!

REM Voltar para diretório raiz
cd ..

REM Iniciar frontend
echo ⚛️  Iniciando frontend React...
cd frontend
start "AutomationX9X Frontend" /min cmd /c "npm start && pause"

REM Aguardar frontend inicializar
timeout /t 8 /nobreak >nul

echo ✅ Frontend iniciado!

echo.
echo 🎉 AutomationX9X iniciado com sucesso!
echo ======================================
echo.
echo 🌐 Acesse o sistema:
echo   Frontend:     http://localhost:3000
echo   Backend API:  http://localhost:8000
echo   Documentação: http://localhost:8000/docs
echo.
echo 💡 Para parar o sistema, feche as janelas do terminal abertas
echo    ou pressione Ctrl+C nas janelas do Backend e Frontend
echo.

REM Abrir o navegador automaticamente
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo 🌐 Abrindo navegador...
echo.
echo ✨ Sistema pronto para uso!
pause