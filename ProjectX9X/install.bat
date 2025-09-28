@echo off
setlocal enabledelayedexpansion

echo.
echo 🚀 Instalando AutomationX9X...
echo ================================
echo.

REM Verificar se está no diretório correto
if not exist "backend" (
    echo ❌ Diretório 'backend' não encontrado!
    echo Execute este script do diretório raiz do projeto.
    echo.
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ Diretório 'frontend' não encontrado!
    echo Execute este script do diretório raiz do projeto.
    echo.
    pause
    exit /b 1
)

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Por favor, instale Python 3.8+ primeiro.
    echo Download: https://python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Verificar se Node.js está instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js não encontrado. Por favor, instale Node.js 16+ primeiro.
    echo Download: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo ✅ Python e Node.js encontrados!
echo.

REM Criar arquivo requirements.txt se não existir
if not exist "backend\requirements.txt" (
    echo 📝 Criando requirements.txt...
    echo fastapi==0.104.1 > backend\requirements.txt
    echo uvicorn[standard]==0.24.0 >> backend\requirements.txt
    echo pydantic==2.5.0 >> backend\requirements.txt
    echo openai==1.3.0 >> backend\requirements.txt
    echo python-multipart==0.0.6 >> backend\requirements.txt
    echo python-dotenv==1.0.0 >> backend\requirements.txt
    echo requests==2.31.0 >> backend\requirements.txt
    echo aiofiles==23.2.1 >> backend\requirements.txt
    echo aiohttp==3.9.0 >> backend\requirements.txt
)

REM Instalar backend
echo 📦 Instalando dependências do backend...
cd backend

REM Criar ambiente virtual Python
echo Criando ambiente virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Erro ao criar ambiente virtual Python
    echo.
    pause
    exit /b 1
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Verificar se requirements.txt existe
if not exist "requirements.txt" (
    echo ❌ Arquivo requirements.txt não encontrado em backend/
    echo.
    pause
    exit /b 1
)

REM Instalar dependências
echo Instalando dependências Python...
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependências do backend
    echo Verifique sua conexão com a internet
    echo.
    pause
    exit /b 1
)

echo ✅ Backend instalado com sucesso!
echo.

REM Voltar para o diretório raiz
cd ..

REM Criar package.json se não existir
if not exist "frontend\package.json" (
    echo 📝 Criando package.json...
    echo { > frontend\package.json
    echo   "name": "automationx9x-frontend", >> frontend\package.json
    echo   "version": "1.0.0", >> frontend\package.json
    echo   "private": true, >> frontend\package.json
    echo   "dependencies": { >> frontend\package.json
    echo     "react": "^18.2.0", >> frontend\package.json
    echo     "react-dom": "^18.2.0", >> frontend\package.json
    echo     "react-scripts": "5.0.1", >> frontend\package.json
    echo     "axios": "^1.6.0" >> frontend\package.json
    echo   }, >> frontend\package.json
    echo   "scripts": { >> frontend\package.json
    echo     "start": "react-scripts start", >> frontend\package.json
    echo     "build": "react-scripts build" >> frontend\package.json
    echo   }, >> frontend\package.json
    echo   "devDependencies": { >> frontend\package.json
    echo     "tailwindcss": "^3.3.6", >> frontend\package.json
    echo     "postcss": "^8.4.32", >> frontend\package.json
    echo     "autoprefixer": "^10.4.16" >> frontend\package.json
    echo   } >> frontend\package.json
    echo } >> frontend\package.json
)

REM Instalar frontend
echo 📦 Instalando dependências do frontend...
cd frontend

REM Instalar dependências Node.js
echo Instalando dependências React...
npm install

if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependências do frontend
    echo Verifique sua conexão com a internet
    echo.
    pause
    exit /b 1
)

REM Instalar Tailwind CSS
echo 🎨 Configurando Tailwind CSS...
npm install -D tailwindcss@latest postcss@latest autoprefixer@latest

REM Inicializar configuração do Tailwind
if not exist "tailwind.config.js" (
    echo Inicializando Tailwind CSS...
    npx tailwindcss init -p
)

echo ✅ Frontend instalado com sucesso!
echo.

REM Voltar para o diretório raiz
cd ..

REM Criar arquivo .env se não existir
if not exist "backend\.env" (
    echo 📝 Criando arquivo .env...
    echo # Configurações do AutomationX9X > backend\.env
    echo DEBUG=True >> backend\.env
    echo SECRET_KEY=automation-x9x-secret-key-2024 >> backend\.env
    echo LOG_LEVEL=INFO >> backend\.env
    echo DATABASE_URL=automation.db >> backend\.env
    echo API_TIMEOUT=30 >> backend\.env
    echo OPENAI_API_KEY= >> backend\.env
)

echo.
echo 🎉 Instalação concluída com sucesso!
echo ================================
echo.
echo 📋 Arquivos criados:
echo - backend\requirements.txt
echo - backend\.env
echo - frontend\package.json
echo - frontend\tailwind.config.js
echo - frontend\postcss.config.js
echo.
echo 📋 Próximos passos:
echo 1. Configure sua chave OpenAI em backend\.env (opcional)
echo 2. Execute: scripts\start.bat
echo.
echo 📚 URLs que estarão disponíveis:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000
echo - Documentação: http://localhost:8000/docs
echo.
pause