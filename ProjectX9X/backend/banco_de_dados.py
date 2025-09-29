"""
Script para atualizar estrutura do banco de dados
Adiciona: categorias, marcas, condições, especificações
"""

import sqlite3

def atualizar_banco():
    conn = sqlite3.connect("automation.db")
    cursor = conn.cursor()
    
    # 1. Criar tabela de categorias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 2. Criar tabela de marcas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marcas (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 3. Atualizar tabela de produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos_novo (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            categoria_id TEXT,
            marca_id TEXT,
            preco REAL DEFAULT 0.0,
            descricao TEXT,
            especificacoes TEXT,
            condicao TEXT DEFAULT 'novo',
            estoque INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id),
            FOREIGN KEY (marca_id) REFERENCES marcas(id)
        )
    """)
    
    # 4. Migrar dados existentes (se houver)
    try:
        cursor.execute("""
            INSERT INTO produtos_novo (id, nome, preco, descricao, estoque, criado_em)
            SELECT id, nome, preco, descricao, estoque, criado_em 
            FROM produtos
        """)
        
        # Renomear tabelas
        cursor.execute("DROP TABLE produtos")
        cursor.execute("ALTER TABLE produtos_novo RENAME TO produtos")
        
    except:
        # Se produtos_novo já existe, só renomear
        try:
            cursor.execute("DROP TABLE produtos")
            cursor.execute("ALTER TABLE produtos_novo RENAME TO produtos")
        except:
            pass
    
    # 5. Inserir categorias padrão
    categorias_padrao = [
        ('cat_celular', 'Celulares e Smartphones', 'Dispositivos móveis'),
        ('cat_tablet', 'Tablets', 'Tablets e iPads'),
        ('cat_acessorio', 'Acessórios', 'Capas, fones, carregadores'),
        ('cat_notebook', 'Notebooks', 'Computadores portáteis'),
        ('cat_smartwatch', 'Smartwatches', 'Relógios inteligentes')
    ]
    
    for cat_id, nome, desc in categorias_padrao:
        try:
            cursor.execute("INSERT OR IGNORE INTO categorias (id, nome, descricao) VALUES (?, ?, ?)", 
                         (cat_id, nome, desc))
        except:
            pass
    
    # 6. Inserir marcas padrão
    marcas_padrao = [
        ('marca_apple', 'Apple'),
        ('marca_samsung', 'Samsung'),
        ('marca_xiaomi', 'Xiaomi'),
        ('marca_motorola', 'Motorola'),
        ('marca_lg', 'LG'),
        ('marca_google', 'Google'),
        ('marca_oneplus', 'OnePlus')
    ]
    
    for marca_id, nome in marcas_padrao:
        try:
            cursor.execute("INSERT OR IGNORE INTO marcas (id, nome) VALUES (?, ?)", 
                         (marca_id, nome))
        except:
            pass
    
    conn.commit()
    conn.close()
    
    print("✅ Banco de dados atualizado!")
    print("📁 Categorias e marcas criadas")
    print("📦 Estrutura de produtos atualizada")

if __name__ == "__main__":
    atualizar_banco()