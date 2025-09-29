"""
Sistema de conversação com Ollama + Busca Web
"""

import requests
from typing import List, Dict, Optional
from duckduckgo_search import DDGS

OLLAMA_URL = "http://localhost:11434/api/chat"
MODELO = "gemma3:4b"

historicos = {}

def buscar_especificacoes_web(produto_nome: str) -> Optional[str]:
    """Busca especificações do produto na web"""
    try:
        print(f"🔍 Buscando specs: {produto_nome}")
        
        with DDGS() as ddgs:
            query = f"{produto_nome} especificações técnicas características"
            resultados = list(ddgs.text(query, max_results=2))
            
            if resultados:
                specs = []
                for r in resultados:
                    specs.append(r.get('body', '')[:200])
                
                specs_texto = " | ".join(specs)
                print(f"✅ Specs encontradas: {specs_texto[:100]}...")
                return specs_texto
        
        return None
    except Exception as e:
        print(f"⚠️ Erro busca web: {e}")
        return None

def preparar_info_produtos(produtos: List[Dict]) -> str:
    """Prepara informações detalhadas dos produtos"""
    
    if not produtos:
        return "Nenhum produto disponível."
    
    produtos_texto = "PRODUTOS DISPONÍVEIS:\n\n"
    
    for p in produtos:
        # Informações básicas
        nome = p.get('nome', 'Sem nome')
        preco = p.get('preco', 0)
        estoque = p.get('estoque', 0)
        condicao = p.get('condicao', 'novo')
        
        # Categoria e marca
        categoria = p.get('categoria_nome', 'Sem categoria')
        marca = p.get('marca_nome', 'Sem marca')
        
        # Descrição e especificações
        descricao = p.get('descricao', '')
        specs = p.get('especificacoes', '')
        
        # Montar texto do produto
        produtos_texto += f"📱 {nome}\n"
        produtos_texto += f"   Marca: {marca} | Categoria: {categoria}\n"
        produtos_texto += f"   Preço: R$ {preco:.2f}\n"
        produtos_texto += f"   Condição: {condicao} | Estoque: {estoque}\n"
        
        if descricao:
            produtos_texto += f"   Descrição: {descricao[:100]}\n"
        
        if specs:
            produtos_texto += f"   Specs: {specs[:150]}\n"
        
        produtos_texto += "\n"
    
    return produtos_texto

def criar_prompt_sistema(loja: str, vendedor: str) -> str:
    """Prompt do sistema"""
    return f"""Você é {vendedor}, vendedor experiente da {loja}.

COMPORTAMENTO:
- Mantenha contexto da conversa (use o histórico)
- Respostas curtas (30-40 palavras)
- Natural como humano
- SEM emojis excessivos (apenas 1 por mensagem se necessário)

CONHECIMENTO:
- Você TEM as informações de produtos (marca, condição, especificações)
- Use essas informações para responder bem
- Se cliente perguntar características, cite as especificações técnicas

MEMÓRIA:
- Lembre do que foi dito antes
- "sim", "qual preço", "me interessa" = cliente referindo ao último produto mencionado

LIMITAÇÕES:
- Se produto não existe: seja honesto
- Se cliente quer encomendar: diga que vai chamar um humano
- Não invente informações"""

def processar_mensagem(texto: str, usuario_id: str, produtos: List[Dict], loja: str, vendedor: str) -> str:
    """Processa mensagem COM contexto e busca web se necessário"""
    
    if usuario_id not in historicos:
        historicos[usuario_id] = []
    
    historico = historicos[usuario_id]
    
    # Verificar se precisa buscar specs na web
    produtos_enriquecidos = produtos.copy()
    
    for produto in produtos_enriquecidos:
        # Se não tem especificações OU são muito curtas
        specs = produto.get('especificacoes', '')
        if not specs or len(specs) < 50:
            # Buscar na web apenas se cliente mencionou esse produto
            if produto['nome'].lower() in texto.lower():
                specs_web = buscar_especificacoes_web(produto['nome'])
                if specs_web:
                    produto['especificacoes'] = specs_web
    
    # Preparar info dos produtos
    produtos_texto = preparar_info_produtos(produtos_enriquecidos)
    
    # Montar mensagens
    mensagens = [
        {
            "role": "system",
            "content": f"{criar_prompt_sistema(loja, vendedor)}\n\n{produtos_texto}"
        }
    ]
    
    # Adicionar histórico
    for msg in historico:
        mensagens.append(msg)
    
    # Mensagem atual
    mensagens.append({
        "role": "user",
        "content": texto
    })
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "messages": mensagens,
                "stream": False,
                "options": {
                    "temperature": 0.4,
                    "num_predict": 100
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            resposta = response.json()["message"]["content"].strip()
            
            # Limpar resposta
            resposta = resposta.split("\n")[0][:250]
            
            # Salvar no histórico
            historico.append({"role": "user", "content": texto})
            historico.append({"role": "assistant", "content": resposta})
            
            # Manter últimas 10 mensagens
            if len(historico) > 10:
                historicos[usuario_id] = historico[-10:]
            
            return resposta
        else:
            return "Desculpe, tive um problema. Pode repetir?"
            
    except Exception as e:
        print(f"Erro Ollama: {e}")
        return "Ops, deu erro. Tenta de novo?"

def limpar_historico(usuario_id: str):
    """Limpa histórico de um usuário"""
    if usuario_id in historicos:
        del historicos[usuario_id]