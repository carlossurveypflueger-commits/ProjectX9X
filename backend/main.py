from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import uuid
from typing import Optional, List
from contextlib import contextmanager

# Importar APENAS o que existe em conversa_ollama
from conversa_ollama import processar_mensagem, limpar_historico

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
    print(f"🚀 {NOME_LOJA} - Sistema Completo Iniciado")
    print(f"👤 Vendedor: {NOME_VENDEDOR}")
    print(f"🌐 Backend: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs")

@app.get("/")
async def root():
    return {
        "nome": NOME_LOJA, 
        "vendedor": NOME_VENDEDOR,
        "status": "funcionando",
        "funcionalidades": [
            "Chat com IA + Busca Web",
            "Detecção de encomendas",
            "Gestão de produtos",
            "Histórico completo"
        ]
    }

@app.post("/mensagem")
async def processar(mensagem: Mensagem):
    try:
        # Buscar todos os produtos
        produtos = obter_produtos_completos()
        
        # Processar com IA (SEMPRE retorna tupla: resposta, transferir)
        try:
            resultado = processar_mensagem(
                mensagem.texto,
                mensagem.usuario_id,
                produtos,
                NOME_LOJA,
                NOME_VENDEDOR
            )
            
            # Garantir que é tupla
            if isinstance(resultado, tuple) and len(resultado) == 2:
                resposta, transferir = resultado
            else:
                # Fallback: se não for tupla, considerar como string
                resposta = str(resultado)
                transferir = False
                
        except ValueError as ve:
            print(f"⚠️ Erro ao desempacotar resultado: {ve}")
            resposta = "Ops, tive um problema. Pode repetir?"
            transferir = False
        
        # Salvar histórico
        with get_db() as conn:
            conn.execute("""
                INSERT INTO historico_mensagens (id, texto, origem, usuario_id, resposta)
                VALUES (?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), mensagem.texto, mensagem.origem, mensagem.usuario_id, resposta))
            conn.commit()
        
        # Se transferir=True, loggar mas NÃO mostrar ao cliente
        if transferir:
            print(f"\n{'='*60}")
            print(f"🚨 AÇÃO NECESSÁRIA: Cliente {mensagem.usuario_id} quer encomendar!")
            print(f"   📱 Mensagem: {mensagem.texto}")
            print(f"   💬 Resposta: {resposta}")
            print(f"   ⏰ Timestamp: {uuid.uuid4()}")
            print(f"{'='*60}\n")
            # Aqui você pode chamar webhook, enviar email, notificar Slack, etc.
        
        return RespostaMensagem(
            sucesso=True, 
            mensagem=resposta, 
            transferir_humano=transferir
        )
        
    except Exception as e:
        print(f"❌ Erro ao processar mensagem: {e}")
        import traceback
        traceback.print_exc()
        return RespostaMensagem(
            sucesso=False, 
            mensagem="Ops! Tive um problema técnico. Pode tentar novamente?"
        )

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

@app.delete("/historico/{usuario_id}")
async def limpar_historico_usuario(usuario_id: str):
    """Limpa histórico de conversa de um usuário"""
    limpar_historico(usuario_id)
    return {"mensagem": f"Histórico do usuário {usuario_id} limpo!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)