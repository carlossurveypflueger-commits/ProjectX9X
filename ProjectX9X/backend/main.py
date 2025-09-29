from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import uuid
from typing import Optional, List
from contextlib import contextmanager
from conversa_ollama import processar_mensagem
from conversa_ollama import limpar_historico

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NOME_LOJA = "HG Phones"
NOME_VENDEDOR = "Alex"

class Mensagem(BaseModel):
    texto: str
    origem: str = "web"
    usuario_id: str = "user"

class DadoProduto(BaseModel):
    nome: str
    categoria_id: Optional[str] = None
    marca_id: Optional[str] = None
    preco: float = 0.0
    descricao: str = ""
    especificacoes: Optional[str] = None
    condicao: str = "novo"
    estoque: int = 0

class Categoria(BaseModel):
    nome: str
    descricao: Optional[str] = ""

class Marca(BaseModel):
    nome: str
    descricao: Optional[str] = ""

class RespostaMensagem(BaseModel):
    sucesso: bool
    mensagem: str
    transferir_humano: bool = False

@contextmanager
def get_db():
    conn = sqlite3.connect("automation.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def obter_produtos_completos():
    """Retorna produtos com categoria, marca e condição"""
    with get_db() as conn:
        produtos = conn.execute("""
            SELECT 
                p.*,
                c.nome as categoria_nome,
                m.nome as marca_nome
            FROM produtos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN marcas m ON p.marca_id = m.id
            WHERE p.ativo = 1
            ORDER BY p.nome
        """).fetchall()
        return [dict(p) for p in produtos]

@app.on_event("startup")
async def startup():
    print(f"🚀 {NOME_LOJA} - Sistema Completo")

@app.get("/")
async def root():
    return {"nome": NOME_LOJA, "status": "funcionando"}

@app.post("/mensagem")
async def processar(mensagem: Mensagem):
    try:
        produtos = obter_produtos_completos()
        
        # Detectar intenção de encomenda
        texto_lower = mensagem.texto.lower()
        palavras_encomenda = ['encomendar', 'pedir', 'trazer', 'conseguir', 'importar', 'buscar para mim']
        transferir = any(palavra in texto_lower for palavra in palavras_encomenda)
        
        resposta = processar_mensagem(
            mensagem.texto,
            mensagem.usuario_id,
            produtos,
            NOME_LOJA,
            NOME_VENDEDOR
        )
        
        # Se detectou intenção de encomenda
        if transferir:
            resposta = "Vou transferir você para um atendente humano que pode ajudar com encomendas especiais!"
        
        # Salvar histórico
        with get_db() as conn:
            conn.execute("""
                INSERT INTO historico_mensagens (id, texto, origem, usuario_id, resposta)
                VALUES (?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), mensagem.texto, mensagem.origem, mensagem.usuario_id, resposta))
            conn.commit()
        
        return RespostaMensagem(sucesso=True, mensagem=resposta, transferir_humano=transferir)
    except Exception as e:
        print(f"Erro: {e}")
        return RespostaMensagem(sucesso=False, mensagem="Ops! Tenta de novo?")

# ROTAS DE CATEGORIAS
@app.get("/categorias")
async def listar_categorias():
    with get_db() as conn:
        return [dict(c) for c in conn.execute("SELECT * FROM categorias ORDER BY nome").fetchall()]

@app.post("/categorias")
async def criar_categoria(categoria: Categoria):
    cat_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute("INSERT INTO categorias (id, nome, descricao) VALUES (?, ?, ?)",
                    (cat_id, categoria.nome, categoria.descricao))
        conn.commit()
    return {"id": cat_id, "mensagem": "Categoria criada!"}

# ROTAS DE MARCAS
@app.get("/marcas")
async def listar_marcas():
    with get_db() as conn:
        return [dict(m) for m in conn.execute("SELECT * FROM marcas ORDER BY nome").fetchall()]

@app.post("/marcas")
async def criar_marca(marca: Marca):
    marca_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute("INSERT INTO marcas (id, nome, descricao) VALUES (?, ?, ?)",
                    (marca_id, marca.nome, marca.descricao))
        conn.commit()
    return {"id": marca_id, "mensagem": "Marca criada!"}

# ROTAS DE PRODUTOS
@app.get("/dados/produtos")
async def listar_produtos():
    return obter_produtos_completos()

@app.get("/dados/produtos/{produto_id}")
async def obter_produto(produto_id: str):
    with get_db() as conn:
        produto = conn.execute("""
            SELECT 
                p.*,
                c.nome as categoria_nome,
                m.nome as marca_nome
            FROM produtos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN marcas m ON p.marca_id = m.id
            WHERE p.id = ?
        """, (produto_id,)).fetchone()
        if not produto:
            return {"erro": "Produto não encontrado"}
        return dict(produto)

@app.post("/dados/produtos")
async def criar_produto(produto: DadoProduto):
    produto_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute("""
            INSERT INTO produtos 
            (id, nome, categoria_id, marca_id, preco, descricao, especificacoes, condicao, estoque)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (produto_id, produto.nome, produto.categoria_id, produto.marca_id, 
              produto.preco, produto.descricao, produto.especificacoes, 
              produto.condicao, produto.estoque))
        conn.commit()
    return {"id": produto_id, "mensagem": "Produto criado!"}

@app.put("/dados/produtos/{produto_id}")
async def atualizar_produto(produto_id: str, produto: DadoProduto):
    with get_db() as conn:
        conn.execute("""
            UPDATE produtos 
            SET nome=?, categoria_id=?, marca_id=?, preco=?, descricao=?, 
                especificacoes=?, condicao=?, estoque=?
            WHERE id=?
        """, (produto.nome, produto.categoria_id, produto.marca_id, produto.preco,
              produto.descricao, produto.especificacoes, produto.condicao, 
              produto.estoque, produto_id))
        conn.commit()
    return {"mensagem": "Produto atualizado!"}

@app.delete("/dados/produtos/{produto_id}")
async def deletar_produto(produto_id: str):
    with get_db() as conn:
        # Soft delete
        conn.execute("UPDATE produtos SET ativo=0 WHERE id=?", (produto_id,))
        conn.commit()
    return {"mensagem": "Produto removido!"}

@app.get("/historico")
async def obter_historico(limite: int = 50):
    with get_db() as conn:
        return [dict(h) for h in conn.execute(
            "SELECT * FROM historico_mensagens ORDER BY processado_em DESC LIMIT ?", 
            (limite,)).fetchall()]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)