"""
Modelos de dados e utilitários para o sistema AutomationX9X
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

DATABASE = "automation.db"

@contextmanager
def get_db():
    """Context manager para conexão com banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

class FluxoModel:
    """Modelo para gerenciar fluxos no banco de dados"""
    
    @staticmethod
    def criar(nome: str, descricao: str, gatilho: Dict, acoes: List[Dict], ativo: bool = True) -> str:
        """Cria um novo fluxo"""
        fluxo_id = str(uuid.uuid4())
        
        with get_db() as conn:
            conn.execute("""
                INSERT INTO fluxos (id, nome, descricao, gatilho, acoes, ativo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                fluxo_id,
                nome,
                descricao,
                json.dumps(gatilho),
                json.dumps(acoes),
                ativo
            ))
            conn.commit()
        
        return fluxo_id
    
    @staticmethod
    def listar(apenas_ativos: bool = False) -> List[Dict]:
        """Lista todos os fluxos"""
        with get_db() as conn:
            query = "SELECT * FROM fluxos"
            if apenas_ativos:
                query += " WHERE ativo = 1"
            query += " ORDER BY criado_em DESC"
            
            fluxos = conn.execute(query).fetchall()
            
            resultado = []
            for fluxo in fluxos:
                fluxo_dict = dict(fluxo)
                fluxo_dict['gatilho'] = json.loads(fluxo_dict['gatilho'])
                fluxo_dict['acoes'] = json.loads(fluxo_dict['acoes'])
                resultado.append(fluxo_dict)
            
            return resultado
    
    @staticmethod
    def obter(fluxo_id: str) -> Optional[Dict]:
        """Obtém um fluxo específico"""
        with get_db() as conn:
            fluxo = conn.execute(
                "SELECT * FROM fluxos WHERE id = ?", (fluxo_id,)
            ).fetchone()
            
            if not fluxo:
                return None
            
            fluxo_dict = dict(fluxo)
            fluxo_dict['gatilho'] = json.loads(fluxo_dict['gatilho'])
            fluxo_dict['acoes'] = json.loads(fluxo_dict['acoes'])
            
            return fluxo_dict
    
    @staticmethod
    def atualizar(fluxo_id: str, nome: str, descricao: str, gatilho: Dict, acoes: List[Dict], ativo: bool) -> bool:
        """Atualiza um fluxo existente"""
        with get_db() as conn:
            result = conn.execute("""
                UPDATE fluxos 
                SET nome = ?, descricao = ?, gatilho = ?, acoes = ?, ativo = ?, 
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                nome,
                descricao,
                json.dumps(gatilho),
                json.dumps(acoes),
                ativo,
                fluxo_id
            ))
            
            conn.commit()
            return result.rowcount > 0
    
    @staticmethod
    def deletar(fluxo_id: str) -> bool:
        """Deleta um fluxo"""
        with get_db() as conn:
            result = conn.execute("DELETE FROM fluxos WHERE id = ?", (fluxo_id,))
            conn.commit()
            return result.rowcount > 0

class ProdutoModel:
    """Modelo para gerenciar produtos no banco de dados"""
    
    @staticmethod
    def criar(nome: str, categoria: str = "", preco: float = 0.0, descricao: str = "", 
              estoque: int = 0, metadados: Dict = None) -> str:
        """Cria um novo produto"""
        produto_id = str(uuid.uuid4())
        if metadados is None:
            metadados = {}
        
        with get_db() as conn:
            conn.execute("""
                INSERT INTO produtos (id, nome, categoria, preco, descricao, estoque, metadados)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                produto_id,
                nome,
                categoria,
                preco,
                descricao,
                estoque,
                json.dumps(metadados)
            ))
            conn.commit()
        
        return produto_id
    
    @staticmethod
    def listar() -> List[Dict]:
        """Lista todos os produtos"""
        with get_db() as conn:
            produtos = conn.execute(
                "SELECT * FROM produtos ORDER BY nome"
            ).fetchall()
            
            resultado = []
            for produto in produtos:
                produto_dict = dict(produto)
                produto_dict['metadados'] = json.loads(produto_dict['metadados']) if produto_dict['metadados'] else {}
                resultado.append(produto_dict)
            
            return resultado
    
    @staticmethod
    def buscar(termo: str) -> List[Dict]:
        """Busca produtos por termo"""
        with get_db() as conn:
            produtos = conn.execute("""
                SELECT * FROM produtos 
                WHERE nome LIKE ? OR descricao LIKE ? OR categoria LIKE ?
                ORDER BY nome
            """, (f"%{termo}%", f"%{termo}%", f"%{termo}%")).fetchall()
            
            resultado = []
            for produto in produtos:
                produto_dict = dict(produto)
                produto_dict['metadados'] = json.loads(produto_dict['metadados']) if produto_dict['metadados'] else {}
                resultado.append(produto_dict)
            
            return resultado
    
    @staticmethod
    def obter(produto_id: str) -> Optional[Dict]:
        """Obtém um produto específico"""
        with get_db() as conn:
            produto = conn.execute(
                "SELECT * FROM produtos WHERE id = ?", (produto_id,)
            ).fetchone()
            
            if not produto:
                return None
            
            produto_dict = dict(produto)
            produto_dict['metadados'] = json.loads(produto_dict['metadados']) if produto_dict['metadados'] else {}
            
            return produto_dict
    
    @staticmethod
    def atualizar(produto_id: str, nome: str, categoria: str = "", preco: float = 0.0, 
                  descricao: str = "", estoque: int = 0, metadados: Dict = None) -> bool:
        """Atualiza um produto existente"""
        if metadados is None:
            metadados = {}
        
        with get_db() as conn:
            result = conn.execute("""
                UPDATE produtos 
                SET nome = ?, categoria = ?, preco = ?, descricao = ?, estoque = ?, metadados = ?
                WHERE id = ?
            """, (
                nome,
                categoria,
                preco,
                descricao,
                estoque,
                json.dumps(metadados),
                produto_id
            ))
            
            conn.commit()
            return result.rowcount > 0
    
    @staticmethod
    def deletar(produto_id: str) -> bool:
        """Deleta um produto"""
        with get_db() as conn:
            result = conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
            conn.commit()
            return result.rowcount > 0

class HistoricoModel:
    """Modelo para gerenciar histórico de mensagens"""
    
    @staticmethod
    def salvar(texto: str, origem: str, usuario_id: str, resposta: str, 
               fluxo_executado: Optional[str] = None, acoes_executadas: List[str] = None) -> str:
        """Salva uma entrada no histórico"""
        if acoes_executadas is None:
            acoes_executadas = []
        
        historico_id = str(uuid.uuid4())
        
        with get_db() as conn:
            conn.execute("""
                INSERT INTO historico_mensagens 
                (id, texto, origem, usuario_id, resposta, fluxo_executado, acoes_executadas)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                historico_id,
                texto,
                origem,
                usuario_id,
                resposta,
                fluxo_executado,
                json.dumps(acoes_executadas)
            ))
            conn.commit()
        
        return historico_id
    
    @staticmethod
    def listar(limite: int = 50, usuario_id: Optional[str] = None) -> List[Dict]:
        """Lista o histórico de mensagens"""
        with get_db() as conn:
            query = "SELECT * FROM historico_mensagens"
            params = []
            
            if usuario_id:
                query += " WHERE usuario_id = ?"
                params.append(usuario_id)
            
            query += " ORDER BY processado_em DESC LIMIT ?"
            params.append(limite)
            
            historico = conn.execute(query, params).fetchall()
            
            resultado = []
            for item in historico:
                item_dict = dict(item)
                item_dict['acoes_executadas'] = json.loads(item_dict['acoes_executadas']) if item_dict['acoes_executadas'] else []
                resultado.append(item_dict)
            
            return resultado
    
    @staticmethod
    def estatisticas() -> Dict:
        """Obtém estatísticas do histórico"""
        with get_db() as conn:
            # Total de mensagens
            total_mensagens = conn.execute("SELECT COUNT(*) FROM historico_mensagens").fetchone()[0]
            
            # Mensagens por dia (últimos 7 dias)
            mensagens_por_dia = conn.execute("""
                SELECT DATE(processado_em) as data, COUNT(*) as total
                FROM historico_mensagens
                WHERE processado_em >= datetime('now', '-7 days')
                GROUP BY DATE(processado_em)
                ORDER BY data DESC
            """).fetchall()
            
            # Fluxos mais utilizados
            fluxos_populares = conn.execute("""
                SELECT fluxo_executado, COUNT(*) as total
                FROM historico_mensagens
                WHERE fluxo_executado IS NOT NULL
                GROUP BY fluxo_executado
                ORDER BY total DESC
                LIMIT 10
            """).fetchall()
            
            return {
                'total_mensagens': total_mensagens,
                'mensagens_por_dia': [dict(row) for row in mensagens_por_dia],
                'fluxos_populares': [dict(row) for row in fluxos_populares]
            }

def criar_exemplos_iniciais():
    """Cria dados de exemplo para demonstração"""
    
    # Criar produtos de exemplo
    produtos_exemplo = [
        {
            'nome': 'iPhone 15 Pro',
            'categoria': 'Smartphones',
            'preco': 7999.99,
            'descricao': 'Smartphone Apple iPhone 15 Pro 128GB - Titânio Natural',
            'estoque': 10,
            'metadados': {'marca': 'Apple', 'cor': 'Titânio Natural', 'armazenamento': '128GB'}
        },
        {
            'nome': 'Samsung Galaxy S24',
            'categoria': 'Smartphones',
            'preco': 4499.99,
            'descricao': 'Samsung Galaxy S24 256GB - Preto',
            'estoque': 15,
            'metadados': {'marca': 'Samsung', 'cor': 'Preto', 'armazenamento': '256GB'}
        },
        {
            'nome': 'Camiseta Polo',
            'categoria': 'Roupas',
            'preco': 79.90,
            'descricao': 'Camiseta Polo masculina 100% algodão',
            'estoque': 50,
            'metadados': {'tamanhos': ['P', 'M', 'G', 'GG'], 'material': 'Algodão'}
        },
        {
            'nome': 'Honda Civic',
            'categoria': 'Veículos',
            'preco': 125000.00,
            'descricao': 'Honda Civic 2024 - Touring 1.5 Turbo CVT',
            'estoque': 3,
            'metadados': {'ano': 2024, 'combustivel': 'Flex', 'cambio': 'Automático'}
        }
    ]
    
    # Verificar se já existem produtos
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
        
        if count == 0:
            for produto in produtos_exemplo:
                ProdutoModel.criar(**produto)
            print("Produtos de exemplo criados!")

if __name__ == "__main__":
    criar_exemplos_iniciais()