from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import json
import uuid
import random
import os
from typing import Dict, List, Optional
from contextlib import contextmanager
from dotenv import load_dotenv
load_dotenv()

# Importar Groq
try:
    from groq import Groq
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None
except ImportError:
    groq_client = None

app = FastAPI(title="AutomationX9X")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Mensagem(BaseModel):
    texto: str
    origem: str = "web"
    usuario_id: str = "anonimo"

class DadoProduto(BaseModel):
    nome: str
    categoria: str = ""
    preco: float = 0.0
    descricao: str = ""
    estoque: int = 0

class RespostaMensagem(BaseModel):
    sucesso: bool
    mensagem: str

@contextmanager
def get_db():
    conn = sqlite3.connect("automation.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                categoria TEXT,
                preco REAL DEFAULT 0.0,
                descricao TEXT,
                estoque INTEGER DEFAULT 0,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS historico_mensagens (
                id TEXT PRIMARY KEY,
                texto TEXT NOT NULL,
                origem TEXT DEFAULT 'web',
                usuario_id TEXT DEFAULT 'anonimo',
                resposta TEXT,
                processado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def processar_mensagem_com_ia(texto: str) -> str:
    """Processa mensagem usando IA para entender intenção"""
    
    print(f"=== DEBUG ===")
    print(f"Texto recebido: {texto}")
    
    # Buscar produtos disponíveis
    with get_db() as conn:
        produtos = conn.execute("SELECT nome, categoria, preco, descricao FROM produtos").fetchall()
    
    if not produtos:
        produtos_info = "NENHUM produto cadastrado."
    else:
        produtos_info = "PRODUTOS DISPONÍVEIS:\n"
        for produto in produtos:
            produtos_info += f"- {produto['nome']} | {produto['categoria']} | R$ {produto['preco']:.2f}\n"
    
    if not groq_client:
        return processar_sem_ia(texto, produtos)
    
    try:
        prompt = f"""Você é um vendedor direto e objetivo. Use APENAS os produtos listados. NÃO invente produtos.

{produtos_info}

Cliente: "{texto}"

REGRAS:
- Seja BREVE (máximo 50 palavras)
- Use APENAS produtos da lista
- NÃO invente produtos
- Seja direto e útil
- Se cumprimentar, responda rápido
- Se perguntar produtos, mostre preços

Resposta curta:"""

        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Seja conciso e direto. Máximo 50 palavras. Use apenas informações fornecidas."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            max_tokens=60,  # Bem reduzido
            temperature=0.2  # Mais conservador
        )
        
        resposta_ia = response.choices[0].message.content.strip()
        
        # Se a resposta for muito longa, cortar
        if len(resposta_ia) > 200:
            resposta_ia = resposta_ia[:200] + "..."
        
        print(f"Resposta da IA: {resposta_ia}")
        return resposta_ia
        
    except Exception as e:
        print(f"ERRO na IA: {e}")
        return processar_sem_ia(texto, produtos)

def processar_sem_ia(texto: str, produtos) -> str:
    """Versão sem IA - respostas curtas"""
    texto_lower = texto.lower()
    
    if any(palavra in texto_lower for palavra in ['oi', 'olá', 'bom dia', 'boa tarde']):
        return "Olá! Como posso ajudar?"
    
    if any(palavra in texto_lower for palavra in ['produto', 'preço', 'quanto', 'valor', 'lista']):
        if produtos:
            resposta = "Produtos disponíveis:\n"
            for produto in produtos:
                resposta += f"• {produto['nome']} - R$ {produto['preco']:.2f}\n"
            return resposta
        else:
            return "Nenhum produto cadastrado."
    
    # Busca específica
    for produto in produtos:
        if any(palavra in produto['nome'].lower() for palavra in texto_lower.split() if len(palavra) > 2):
            return f"{produto['nome']} - R$ {produto['preco']:.2f}\n{produto['categoria']}"
    
    return "Como posso ajudar? Digite 'produtos' para ver nossa lista."

def processar_sem_ia(texto: str, produtos) -> str:
    """Versão sem IA"""
    texto_lower = texto.lower()
    
    if any(palavra in texto_lower for palavra in ['oi', 'olá', 'bom dia', 'boa tarde']):
        return "Olá! Como posso ajudar você hoje?"
    
    if any(palavra in texto_lower for palavra in ['produto', 'preço', 'quanto', 'valor']):
        if produtos:
            resposta = "Temos estes produtos:\n\n"
            for produto in produtos[:3]:
                resposta += f"{produto['nome']} - R$ {produto['preco']:.2f}\n"
            return resposta
        else:
            return "Ainda não temos produtos cadastrados."
    
    return "Como posso ajudar você?"

def processar_mensagem_simples(texto: str) -> str:
    return processar_mensagem_com_ia(texto)

@app.on_event("startup")
async def startup():
    init_database()

@app.get("/")
async def root():
    return {"nome": "AutomationX9X", "status": "funcionando"}

@app.post("/mensagem")
async def processar_mensagem(mensagem: Mensagem):
    try:
        print(f"\n=== NOVA MENSAGEM ===")
        print(f"Texto: {mensagem.texto}")
        
        resposta = processar_mensagem_simples(mensagem.texto)
        
        print(f"Resposta final: {resposta}")
        print(f"=== FIM ===\n")
        
        with get_db() as conn:
            conn.execute("""
                INSERT INTO historico_mensagens (id, texto, origem, usuario_id, resposta)
                VALUES (?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), mensagem.texto, mensagem.origem, mensagem.usuario_id, resposta))
            conn.commit()
        
        return RespostaMensagem(sucesso=True, mensagem=resposta)
    except Exception as e:
        print(f"ERRO GERAL: {e}")
        return RespostaMensagem(sucesso=False, mensagem="Erro ao processar mensagem")

@app.get("/dados/produtos")
async def listar_produtos():
    with get_db() as conn:
        produtos = conn.execute("SELECT * FROM produtos ORDER BY nome").fetchall()
        return [dict(produto) for produto in produtos]

@app.post("/dados/produtos")
async def criar_produto(produto: DadoProduto):
    produto_id = str(uuid.uuid4())
    
    with get_db() as conn:
        conn.execute("""
            INSERT INTO produtos (id, nome, categoria, preco, descricao, estoque)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (produto_id, produto.nome, produto.categoria, produto.preco, produto.descricao, produto.estoque))
        conn.commit()
    
    return {"id": produto_id, "mensagem": "Produto criado com sucesso"}

@app.get("/dados/produtos/{produto_id}")
async def obter_produto(produto_id: str):
    with get_db() as conn:
        produto = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
        if not produto:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        return dict(produto)

@app.put("/dados/produtos/{produto_id}")
async def atualizar_produto(produto_id: str, produto: DadoProduto):
    with get_db() as conn:
        result = conn.execute("""
            UPDATE produtos SET nome = ?, categoria = ?, preco = ?, descricao = ?, estoque = ?
            WHERE id = ?
        """, (produto.nome, produto.categoria, produto.preco, produto.descricao, produto.estoque, produto_id))
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        conn.commit()
    
    return {"mensagem": "Produto atualizado com sucesso"}

@app.delete("/dados/produtos/{produto_id}")
async def deletar_produto(produto_id: str):
    with get_db() as conn:
        result = conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        conn.commit()
    
    return {"mensagem": "Produto deletado com sucesso"}

@app.get("/historico")
async def obter_historico(limite: int = 50):
    with get_db() as conn:
        historico = conn.execute("""
            SELECT * FROM historico_mensagens 
            ORDER BY processado_em DESC 
            LIMIT ?
        """, (limite,)).fetchall()
        return [dict(item) for item in historico]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)