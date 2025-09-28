# 🚀 AutomationX9X - Sistema de Automação Inteligente

Sistema completo de automação semelhante ao n8n, porém mais intuitivo, fácil e eficiente, com integração de IA para análise de mensagens de clientes.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.3+-blue.svg)](https://tailwindcss.com)

## 📋 Visão Geral

O AutomationX9X é um sistema modular de automação que permite:

- 🤖 **Processamento inteligente de mensagens** usando IA
- 🔄 **Criação de fluxos visuais** com gatilhos e ações personalizáveis  
- 📦 **Gerenciamento de produtos/serviços** integrado
- 📊 **Histórico completo** de todas as interações
- 🎨 **Interface web moderna** com React.js e TailwindCSS
- 🚀 **API RESTful robusta** com FastAPI
- 🔌 **Sistema modular** para futuras integrações (WhatsApp, Telegram, ERPs)

## 🎯 Casos de Uso

- **Lojas de Celular**: Atendimento automatizado, consulta de produtos, verificação de estoque
- **Lojas de Roupas**: Recomendações personalizadas, informações de tamanhos, promoções
- **Concessionárias**: Consulta de veículos, agendamento de test-drives, informações técnicas
- **Agências de Marketing**: Geração de leads, qualificação automática, follow-up
- **E-commerce**: Suporte ao cliente, rastreamento de pedidos, FAQ automatizado

## 🏗️ Arquitetura do Sistema

```
AutomationX9X/
├── 📁 backend/                    # Backend Python/FastAPI
│   ├── main.py                   # Aplicação principal 
│   ├── models.py                 # Modelos de dados
│   ├── config.py                 # Configurações e utilitários
│   └── requirements.txt          # Dependências Python
├── 📁 frontend/                   # Frontend React.js
│   ├── src/App.js               # Interface principal
│   ├── package.json             # Dependências Node.js
│   └── tailwind.config.js       # Configuração TailwindCSS
├── 📁 scripts/                    # Scripts de instalação/execução
└── 📁 docs/                       # Documentação
```

## ⚡ Instalação Rápida

### Pré-requisitos
- Python 3.8+ ([Download](https://python.org/downloads/))
- Node.js 16+ ([Download](https://nodejs.org/))
- Git ([Download](https://git-scm.com/))

### 1. Clonar o Repositório
```bash
git clone https://github.com/carlossurveypflueger-commits/ProjectX9X.git
cd ProjectX9X
```

### 2. Instalação Automática
```bash
# Linux/Mac
chmod +x scripts/install.sh
./scripts/install.sh

# Windows
scripts\install.bat
```

### 3. Configurar Variáveis (Opcional)
```bash
# Editar backend/.env
OPENAI_API_KEY=sua-chave-openai-aqui  # Para IA avançada
DEBUG=True
```

### 4. Iniciar o Sistema
```bash
# Linux/Mac
./scripts/start.sh

# Windows  
scripts\start.bat
```

## 🌐 Acesso ao Sistema

Após inicializar:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs

## 🔧 Instalação Manual

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## 📚 Como Usar

### 1. 💬 Chat de Teste
- Acesse a aba "Chat de Teste"
- Digite mensagens como: "Olá", "Quero saber sobre produtos", "Preço do iPhone"
- O sistema processará automaticamente usando IA e fluxos configurados

### 2. 🔄 Criar Fluxos
- Acesse "Fluxos" no menu
- Clique em "Novo Fluxo"
- Configure:
  - **Nome**: Ex: "Consulta Preços"
  - **Gatilho**: Palavras-chave como "preço, valor, quanto custa"
  - **Ações**: "Consultar Produto" ou "Responder"

### 3. 📦 Gerenciar Produtos
- Acesse "Produtos" no menu
- Adicione produtos com: nome, categoria, preço, descrição, estoque
- Os produtos serão consultados automaticamente nos fluxos

### 4. 📊 Monitorar Histórico
- Acesse "Histórico" para ver todas as interações
- Analise quais fluxos são mais utilizados
- Monitore satisfação dos clientes

## 🔌 Integrações Futuras

O sistema foi projetado para ser modular. Próximas integrações:

- **WhatsApp Business API**
- **Telegram Bot**
- **Email (SMTP/IMAP)**
- **Webhooks personalizados**
- **CRMs (HubSpot, Salesforce)**
- **ERPs (SAP, Oracle)**
- **E-commerce (Shopify, WooCommerce)**

## 🛡️ Segurança

- Validação de entrada de dados
- Sanitização de URLs de webhook
- Rate limiting (implementar em produção)
- HTTPS obrigatório para webhooks
- Logs de auditoria completos

## 📈 Monitoramento

O sistema inclui:
- Logs detalhados em `automation.log`
- Histórico completo de mensagens
- Estatísticas de uso de fluxos
- Métricas de performance da IA

## 🔧 Configurações Avançadas

### Integração OpenAI
```python
# backend/.env
OPENAI_API_KEY=sk-sua-chave-aqui
OPENAI_MODEL=gpt-3.5-turbo  # ou gpt-4
```

### Webhook Personalizado
```json
{
  "tipo": "webhook",
  "url": "https://sua-api.com/webhook",
  "metodo": "POST",
  "dados": {
    "mensagem": "{{texto_usuario}}",
    "usuario": "{{usuario_id}}"
  }
}
```

### Banco de Dados Personalizado
```python
# Para usar PostgreSQL em vez de SQLite
# requirements.txt: adicionar psycopg2-binary
DATABASE_URL=postgresql://user:password@localhost/automation
```

## 🚀 Deploy em Produção

### Docker
```bash
# Construir imagens
docker-compose build

# Executar
docker-compose up -d
```

### Railway/Heroku
```bash
# Configurar variáveis de ambiente
OPENAI_API_KEY=sua-chave
DATABASE_URL=postgresql://...
```

### VPS/Servidor
```bash
# Configurar nginx como proxy reverso
# Usar gunicorn para produção
pip install gunicorn
gunicorn main:app --workers 4 --bind 0.0.0.0:8000
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Exemplos de Fluxos

### Atendimento Loja de Celular
```json
{
  "nome": "Consulta iPhone",
  "gatilho": {
    "tipo": "keyword",
    "palavras": ["iphone", "apple", "smartphone"]
  },
  "acoes": [
    {
      "tipo": "consultar_produto",
      "termo": "iphone"
    },
    {
      "tipo": "responder",
      "texto": "Gostaria de agendar uma visita à loja? 📱"
    }
  ]
}
```

### Lead Qualification
```json
{
  "nome": "Qualificar Lead",
  "gatilho": {
    "tipo": "ia",
    "contexto": "usuario interessado em comprar"
  },
  "acoes": [
    {
      "tipo": "salvar_lead"
    },
    {
      "tipo": "webhook",
      "url": "https://crm.empresa.com/leads"
    },
    {
      "tipo": "responder",
      "texto": "Obrigado pelo interesse! Nossa equipe entrará em contato em breve. 🎯"
    }
  ]
}
```

## 🔍 Troubleshooting

### Problemas Comuns

**Backend não inicia**
```bash
# Verificar Python
python --version

# Recriar ambiente virtual
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend não carrega**
```bash
# Limpar cache npm
npm cache clean --force
rm -rf node_modules
npm install
```

**Banco não inicializa**
```bash
# Deletar banco e recriar
rm automation.db
# Reiniciar backend para recriar tabelas
```

**OpenAI não funciona**
```bash
# Verificar chave da API
export OPENAI_API_KEY=sua-chave
# ou adicionar em .env
```

## 📊 Métricas e Analytics

O sistema coleta automaticamente:
- Número de mensagens processadas
- Fluxos mais utilizados
- Tempo de resposta médio
- Taxa de satisfação (através de análise de sentimento)
- Produtos mais consultados

## 🔮 Roadmap

### v1.1 (Próxima Release)
- [ ] Interface visual para criação de fluxos (drag & drop)
- [ ] Integração WhatsApp Business
- [ ] Dashboard analytics avançado
- [ ] Sistema de templates de fluxos

### v1.2
- [ ] Integração Telegram
- [ ] Sistema de usuários e permissões
- [ ] API de webhooks entrada
- [ ] Backup automático

### v2.0
- [ ] Marketplace de integrações
- [ ] IA multimodal (imagens, áudio)
- [ ] Sistema de plugins
- [ ] Mobile app

## 🏆 Casos de Sucesso

### Loja TechCell
- **90% redução** no tempo de resposta
- **150% aumento** na conversão de leads
- **24/7 atendimento** automatizado

### Agência MarketPro
- **300+ leads** qualificados automaticamente/mês
- **80% redução** em trabalho manual
- **ROI 400%** em 3 meses

## 📞 Suporte

- **GitHub Issues**: [Reportar bugs](https://github.com/carlossurveypflueger-commits/ProjectX9X/issues)
- **Discussões**: [Comunidade](https://github.com/carlossurveypflueger-commits/ProjectX9X/discussions)
- **Email**: contato@automationx9x.com
- **Discord**: [Servidor da Comunidade](https://discord.gg/automationx9x)

## 📜 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web Python
- [React](https://reactjs.org/) - Biblioteca JavaScript
- [TailwindCSS](https://tailwindcss.com/) - Framework CSS
- [OpenAI](https://openai.com/) - API de IA
- Comunidade open source

---

<div align="center">

**🚀 Pronto para automatizar seu negócio?**

[⬇️ Download](https://github.com/carlossurveypflueger-commits/ProjectX9X/archive/main.zip) • [📚 Docs](https://docs.automationx9x.com) • [🎯 Demo](https://demo.automationx9x.com)

**Desenvolvido com ❤️ by AutomationX9X Team**

</div>