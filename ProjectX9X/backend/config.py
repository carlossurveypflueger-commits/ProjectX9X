"""
Configuração de IA Local para AutomationX9X com Gemma3
"""

import os
from typing import Dict, List

# Configurações da IA Local
OLLAMA_HOST = "http://localhost:11434"
MODELO_IA = "gemma3:4b"  # Modelo Gemma3 4B correto

# Configurações da loja
NOME_LOJA = "HG Phones"
TIPO_LOJA = "telefones celulares"
NOME_VENDEDOR = "Alex"

# Prompts otimizados - Mais inteligentes e naturais
PROMPTS_SISTEMA = {
    "base": f"""Você é {NOME_VENDEDOR}, vendedor experiente da {NOME_LOJA}.

COMO RESPONDER:
- Seja direto e claro
- Se NÃO temos o produto: diga "Não temos [produto] no momento" e sugira similar se houver
- Se TEMOS o produto: confirme e pergunte se quer detalhes
- Máximo 35 palavras
- Use linguagem natural de vendedor real

NUNCA invente produtos que não estão na lista.""",

    "saudacao": f"""Cumprimente de forma amigável e pergunte como pode ajudar.
Exemplo: "E aí! Sou o {NOME_VENDEDOR}. Procurando algum celular?"
Máximo 15 palavras.""",

    "interesse_geral": f"""Cliente quer ver produtos mas não especificou modelo.
PERGUNTE qual marca/modelo prefere antes de listar.
Exemplo: "Beleza! Tem preferência de marca? iPhone, Samsung, Xiaomi?"
Máximo 20 palavras.""",

    "produto_nao_temos": f"""Cliente perguntou produto que NÃO temos.
Seja HONESTO. Diga que não tem e sugira alternativa se houver.
Exemplo: "Não tenho iPhone 17 ainda. Mas tenho iPhone 12. Te interessa?"
Máximo 30 palavras.""",

    "produto_temos": f"""Cliente perguntou produto que TEMOS.
Confirme que tem. NÃO fale preço ainda.
Exemplo: "Tenho iPhone 12 sim! Ótimo aparelho. Quer saber o preço?"
Máximo 25 palavras.""",

    "preco": f"""Cliente perguntou preço específico.
Informe APENAS o preço do produto perguntado.
Exemplo: "iPhone 12 tá R$ 9.999,00. Quer parcelar?"
Máximo 20 palavras.""",

    "especificacoes": f"""Cliente quer saber especificações técnicas.
Forneça informações técnicas disponíveis na descrição do produto.
Se não tiver info completa, seja honesto.
Máximo 40 palavras."""
}

def classificar_intencao(texto: str, produtos: list = None) -> str:
    """Classifica intenção do cliente de forma mais inteligente"""
    texto_lower = texto.lower()
    
    # Saudações iniciais
    if any(p in texto_lower for p in ['oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite', 'hey', 'e ai']):
        return "saudacao"
    
    # Perguntas sobre especificações técnicas
    if any(p in texto_lower for p in ['especificacao', 'caracteristica', 'camera', 'bateria', 'tela', 'memoria', 'processador', 'ficha tecnica']):
        return "especificacoes"
    
    # Perguntas sobre preço ESPECÍFICO
    if any(p in texto_lower for p in ['quanto custa', 'qual o preço', 'quanto é', 'valor do', 'preço do', 'quanto ta']):
        return "preco"
    
    # Verificar se mencionou produto específico
    marcas_modelos = ['iphone', 'samsung', 'galaxy', 'xiaomi', 'redmi', 'motorola', 'moto', 'poco', 'realme', 
                      'iphone 17', 'iphone 16', 'iphone 15', 'iphone 14', 'iphone 13', 'iphone 12',
                      's24', 's23', 's22', 'note', 'a54', 'a34']
    
    produto_mencionado = any(marca in texto_lower for marca in marcas_modelos)
    
    if produto_mencionado:
        # Verificar se temos esse produto
        if produtos:
            tem_produto = any(
                any(palavra in p['nome'].lower() for palavra in texto_lower.split() if len(palavra) > 2)
                for p in produtos
            )
            
            if tem_produto:
                return "produto_temos"
            else:
                return "produto_nao_temos"
        
        return "produto_especifico"
    
    # Pergunta GERAL sobre produtos (sem especificar)
    if any(p in texto_lower for p in ['produto', 'celular', 'smartphone', 'telefone', 'o que tem', 'tem o que', 'quero ver']):
        return "interesse_geral"
    
    return "base"

# Configurações de geração
CONFIGURACAO_IA = {
    "temperature": 0.3,      # Mais consistente
    "num_predict": 80,       # Limite de tokens para respostas curtas
    "top_p": 0.9,
    "top_k": 40,
    "repeat_penalty": 1.2,   # Evitar repetições
    "stop": ["\n\n", "Cliente:", "Vendedor:", "Usuário:"]
}