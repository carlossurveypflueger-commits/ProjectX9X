import React, { useState, useEffect } from 'react';
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [mensagem, setMensagem] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [produtos, setProdutos] = useState([]);
  const [historico, setHistorico] = useState([]);
  const [novoProduto, setNovoProduto] = useState({
    nome: '', categoria: '', preco: 0, descricao: '', estoque: 0
  });
  const [editandoProduto, setEditandoProduto] = useState(null);
  const [loading, setLoading] = useState(false);
  const [conectado, setConectado] = useState(true);

  // Verificar conexão com backend
  useEffect(() => {
    const verificarConexao = async () => {
      try {
        await api.get('/');
        setConectado(true);
      } catch (error) {
        setConectado(false);
      }
    };
    verificarConexao();
  }, []);

  useEffect(() => {
    if (activeTab === 'produtos') {
      carregarProdutos();
    }
    if (activeTab === 'historico') {
      carregarHistorico();
    }
  }, [activeTab]);

  const enviarMensagem = async () => {
    if (!mensagem.trim()) return;

    const msg = mensagem;
    setChatHistory(prev => [...prev, { tipo: 'user', texto: msg, timestamp: Date.now() }]);
    setMensagem('');

    try {
      const response = await api.post('/mensagem', { texto: msg, origem: 'web', usuario_id: 'user' });
      setChatHistory(prev => [...prev, { 
        tipo: 'bot', 
        texto: response.data.mensagem, 
        timestamp: Date.now() 
      }]);
      setConectado(true);
    } catch (error) {
      setChatHistory(prev => [...prev, { 
        tipo: 'error', 
        texto: 'Erro: Verifique se o backend está rodando', 
        timestamp: Date.now() 
      }]);
      setConectado(false);
    }
  };

  const carregarProdutos = async () => {
    try {
      setLoading(true);
      const response = await api.get('/dados/produtos');
      setProdutos(response.data);
    } catch (error) {
      console.error('Erro ao carregar produtos:', error);
    } finally {
      setLoading(false);
    }
  };

  const carregarHistorico = async () => {
    try {
      setLoading(true);
      const response = await api.get('/historico');
      setHistorico(response.data);
    } catch (error) {
      console.error('Erro ao carregar histórico:', error);
    } finally {
      setLoading(false);
    }
  };

  const criarProduto = async () => {
    if (!novoProduto.nome.trim()) {
      alert('Nome é obrigatório');
      return;
    }
    
    try {
      setLoading(true);
      if (editandoProduto) {
        await api.put(`/dados/produtos/${editandoProduto}`, novoProduto);
      } else {
        await api.post('/dados/produtos', novoProduto);
      }
      setNovoProduto({ nome: '', categoria: '', preco: 0, descricao: '', estoque: 0 });
      setEditandoProduto(null);
      await carregarProdutos();
      alert(editandoProduto ? 'Produto atualizado!' : 'Produto criado!');
    } catch (error) {
      alert('Erro ao salvar produto');
    } finally {
      setLoading(false);
    }
  };

  const editarProduto = (produto) => {
    setNovoProduto(produto);
    setEditandoProduto(produto.id);
  };

  const deletarProduto = async (id) => {
    // eslint-disable-next-line no-restricted-globals
    if (!window.confirm('Deletar produto?')) return;
    
    try {
      setLoading(true);
      await api.delete(`/dados/produtos/${id}`);
      await carregarProdutos();
      alert('Produto deletado!');
    } catch (error) {
      alert('Erro ao deletar produto');
    } finally {
      setLoading(false);
    }
  };

  const limparChat = () => {
    setChatHistory([]);
  };

  const renderStatusConexao = () => (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      padding: '8px 12px',
      borderRadius: '20px',
      fontSize: '12px',
      backgroundColor: conectado ? '#22c55e' : '#ef4444',
      color: 'white',
      zIndex: 1000
    }}>
      {conectado ? 'Online' : 'Offline'}
    </div>
  );

  const renderChat = () => (
    <div style={{padding: '20px', maxWidth: '800px', margin: '0 auto'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
        <h2>Chat de Teste</h2>
        <button 
          onClick={limparChat}
          style={{
            padding: '8px 16px',
            backgroundColor: '#6b7280',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '12px'
          }}
        >
          Limpar Chat
        </button>
      </div>
      
      <div style={{
        border: '1px solid #ddd', 
        height: '400px', 
        overflowY: 'auto', 
        padding: '15px', 
        marginBottom: '15px', 
        backgroundColor: '#f9f9f9',
        borderRadius: '8px'
      }}>
        {chatHistory.length === 0 ? (
          <div style={{textAlign: 'center', color: '#666', padding: '50px 0'}}>
            <p>Inicie uma conversa...</p>
            <p style={{fontSize: '12px', marginTop: '10px'}}>
              Experimente: "oi", "preço do iPhone", "produtos disponíveis"
            </p>
          </div>
        ) : (
          chatHistory.map((msg, i) => (
            <div key={i} style={{marginBottom: '12px', textAlign: msg.tipo === 'user' ? 'right' : 'left'}}>
              <div style={{
                display: 'inline-block',
                padding: '10px 15px',
                borderRadius: '12px',
                maxWidth: '70%',
                backgroundColor: msg.tipo === 'user' ? '#3b82f6' : msg.tipo === 'error' ? '#ef4444' : '#fff',
                color: msg.tipo === 'user' || msg.tipo === 'error' ? 'white' : 'black',
                border: msg.tipo === 'bot' ? '1px solid #ddd' : 'none',
                boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                position: 'relative'
              }}>
                {msg.texto}
                <div style={{
                  fontSize: '10px',
                  opacity: 0.7,
                  marginTop: '4px',
                  textAlign: msg.tipo === 'user' ? 'right' : 'left'
                }}>
                  {new Date(msg.timestamp).toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'})}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
      
      <div style={{display: 'flex', gap: '10px'}}>
        <input
          type="text"
          value={mensagem}
          onChange={(e) => setMensagem(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && enviarMensagem()}
          placeholder="Digite sua mensagem..."
          disabled={!conectado}
          style={{
            flex: 1, 
            padding: '12px', 
            border: '1px solid #ddd', 
            borderRadius: '6px',
            fontSize: '14px',
            backgroundColor: conectado ? 'white' : '#f5f5f5'
          }}
        />
        <button 
          onClick={enviarMensagem} 
          disabled={!conectado || !mensagem.trim()}
          style={{
            padding: '12px 24px', 
            backgroundColor: conectado && mensagem.trim() ? '#3b82f6' : '#ccc', 
            color: 'white', 
            border: 'none',
            borderRadius: '6px',
            cursor: conectado && mensagem.trim() ? 'pointer' : 'not-allowed'
          }}
        >
          Enviar
        </button>
      </div>
    </div>
  );

  const renderProdutos = () => (
    <div style={{padding: '20px', maxWidth: '1200px', margin: '0 auto'}}>
      <h2>Gerenciamento de Produtos</h2>
      
      {loading && (
        <div style={{textAlign: 'center', padding: '20px', color: '#666'}}>
          Carregando...
        </div>
      )}
      
      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px'}}>
        <div style={{backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)'}}>
          <h3>{editandoProduto ? 'Editar Produto' : 'Novo Produto'}</h3>
          
          <div style={{display: 'flex', flexDirection: 'column', gap: '10px'}}>
            <input
              type="text"
              value={novoProduto.nome}
              onChange={(e) => setNovoProduto(prev => ({...prev, nome: e.target.value}))}
              placeholder="Nome do produto *"
              style={{padding: '10px', border: '1px solid #ddd', borderRadius: '4px'}}
            />
            
            <input
              type="text"
              value={novoProduto.categoria}
              onChange={(e) => setNovoProduto(prev => ({...prev, categoria: e.target.value}))}
              placeholder="Categoria"
              style={{padding: '10px', border: '1px solid #ddd', borderRadius: '4px'}}
            />
            
            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px'}}>
              <input
                type="number"
                step="0.01"
                value={novoProduto.preco}
                onChange={(e) => setNovoProduto(prev => ({...prev, preco: parseFloat(e.target.value) || 0}))}
                placeholder="Preço"
                style={{padding: '10px', border: '1px solid #ddd', borderRadius: '4px'}}
              />
              <input
                type="number"
                value={novoProduto.estoque}
                onChange={(e) => setNovoProduto(prev => ({...prev, estoque: parseInt(e.target.value) || 0}))}
                placeholder="Estoque"
                style={{padding: '10px', border: '1px solid #ddd', borderRadius: '4px'}}
              />
            </div>
            
            <textarea
              value={novoProduto.descricao}
              onChange={(e) => setNovoProduto(prev => ({...prev, descricao: e.target.value}))}
              placeholder="Descrição"
              rows="3"
              style={{padding: '10px', border: '1px solid #ddd', borderRadius: '4px', resize: 'vertical'}}
            />
            
            <div style={{display: 'flex', gap: '10px'}}>
              <button 
                onClick={criarProduto}
                disabled={loading}
                style={{
                  flex: 1, 
                  padding: '12px', 
                  backgroundColor: loading ? '#ccc' : '#22c55e', 
                  color: 'white', 
                  border: 'none',
                  borderRadius: '6px',
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? 'Salvando...' : (editandoProduto ? 'Atualizar' : 'Criar')}
              </button>
              
              {editandoProduto && (
                <button 
                  onClick={() => {
                    setEditandoProduto(null);
                    setNovoProduto({ nome: '', categoria: '', preco: 0, descricao: '', estoque: 0 });
                  }}
                  style={{
                    padding: '12px 20px', 
                    backgroundColor: '#6b7280', 
                    color: 'white', 
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer'
                  }}
                >
                  Cancelar
                </button>
              )}
            </div>
          </div>
        </div>
        
        <div style={{backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)'}}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px'}}>
            <h3>Produtos ({produtos.length})</h3>
            <button
              onClick={carregarProdutos}
              style={{
                padding: '6px 12px',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              Atualizar
            </button>
          </div>
          
          <div style={{maxHeight: '400px', overflowY: 'auto'}}>
            {produtos.length === 0 ? (
              <p style={{textAlign: 'center', color: '#666', padding: '40px 0'}}>Nenhum produto cadastrado</p>
            ) : (
              produtos.map(produto => (
                <div key={produto.id} style={{
                  border: '1px solid #ddd', 
                  borderRadius: '6px', 
                  padding: '15px', 
                  marginBottom: '10px',
                  backgroundColor: '#fafafa'
                }}>
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'start'}}>
                    <div style={{flex: 1}}>
                      <h4 style={{margin: '0 0 5px 0'}}>{produto.nome}</h4>
                      {produto.categoria && (
                        <p style={{margin: '0 0 5px 0', fontSize: '12px', color: '#666', backgroundColor: '#e5e7eb', display: 'inline-block', padding: '2px 8px', borderRadius: '12px'}}>
                          {produto.categoria}
                        </p>
                      )}
                      <p style={{margin: '5px 0', fontWeight: 'bold', fontSize: '16px', color: '#22c55e'}}>
                        R$ {produto.preco.toFixed(2)}
                      </p>
                      <p style={{margin: '0 0 5px 0', fontSize: '12px'}}>
                        Estoque: <span style={{fontWeight: 'bold', color: produto.estoque > 0 ? '#22c55e' : '#ef4444'}}>{produto.estoque}</span>
                      </p>
                      {produto.descricao && (
                        <p style={{margin: '5px 0 0 0', fontSize: '12px', color: '#666', fontStyle: 'italic'}}>{produto.descricao}</p>
                      )}
                    </div>
                    <div style={{display: 'flex', gap: '5px', marginLeft: '10px'}}>
                      <button
                        onClick={() => editarProduto(produto)}
                        style={{
                          padding: '5px 10px', 
                          fontSize: '12px', 
                          backgroundColor: '#3b82f6',
                          color: 'white', 
                          border: 'none', 
                          borderRadius: '4px', 
                          cursor: 'pointer'
                        }}
                      >
                        Editar
                      </button>
                      <button
                        onClick={() => deletarProduto(produto.id)}
                        style={{
                          padding: '5px 10px', 
                          fontSize: '12px', 
                          backgroundColor: '#ef4444',
                          color: 'white', 
                          border: 'none', 
                          borderRadius: '4px', 
                          cursor: 'pointer'
                        }}
                      >
                        Deletar
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );

  const renderHistorico = () => (
    <div style={{padding: '20px', maxWidth: '1000px', margin: '0 auto'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
        <h2>Histórico de Mensagens</h2>
        <button
          onClick={carregarHistorico}
          style={{
            padding: '8px 16px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '12px'
          }}
        >
          Atualizar
        </button>
      </div>
      
      {loading && (
        <div style={{textAlign: 'center', padding: '20px', color: '#666'}}>
          Carregando histórico...
        </div>
      )}
      
      <div style={{backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflow: 'hidden'}}>
        <table style={{width: '100%', borderCollapse: 'collapse'}}>
          <thead style={{backgroundColor: '#f9fafb'}}>
            <tr>
              <th style={{padding: '12px', textAlign: 'left', fontSize: '12px', color: '#666', fontWeight: 'bold'}}>Data/Hora</th>
              <th style={{padding: '12px', textAlign: 'left', fontSize: '12px', color: '#666', fontWeight: 'bold'}}>Mensagem</th>
              <th style={{padding: '12px', textAlign: 'left', fontSize: '12px', color: '#666', fontWeight: 'bold'}}>Resposta</th>
              <th style={{padding: '12px', textAlign: 'left', fontSize: '12px', color: '#666', fontWeight: 'bold'}}>Usuário</th>
            </tr>
          </thead>
          <tbody>
            {historico.length === 0 ? (
              <tr>
                <td colSpan="4" style={{padding: '40px', textAlign: 'center', color: '#666'}}>
                  Nenhuma mensagem no histórico
                </td>
              </tr>
            ) : (
              historico.map(item => (
                <tr key={item.id} style={{borderTop: '1px solid #eee'}}>
                  <td style={{padding: '12px', fontSize: '13px', color: '#666'}}>
                    {new Date(item.processado_em).toLocaleString('pt-BR')}
                  </td>
                  <td style={{padding: '12px', fontSize: '14px', maxWidth: '200px'}}>
                    <div style={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}} title={item.texto}>
                      {item.texto}
                    </div>
                  </td>
                  <td style={{padding: '12px', fontSize: '14px', maxWidth: '200px'}}>
                    <div style={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}} title={item.resposta}>
                      {item.resposta}
                    </div>
                  </td>
                  <td style={{padding: '12px', fontSize: '13px', color: '#666'}}>
                    {item.usuario_id}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );

  return (
    <div style={{minHeight: '100vh', backgroundColor: '#f3f4f6'}}>
      {renderStatusConexao()}
      
      <header style={{backgroundColor: 'white', boxShadow: '0 1px 3px rgba(0,0,0,0.1)'}}>
        <div style={{maxWidth: '1200px', margin: '0 auto', padding: '0 24px', height: '64px', display: 'flex', alignItems: 'center'}}>
          <h1 style={{fontSize: '20px', fontWeight: 'bold', margin: 0, color: '#1f2937'}}>AutomationX9X</h1>
          <span style={{marginLeft: '8px', fontSize: '14px', color: '#666'}}>Sistema de Automação Inteligente</span>
        </div>
      </header>

      <nav style={{backgroundColor: 'white', borderBottom: '1px solid #eee'}}>
        <div style={{maxWidth: '1200px', margin: '0 auto', padding: '0 24px', display: 'flex', gap: '32px'}}>
          {[
            {key: 'chat', label: 'Chat de Teste'},
            {key: 'produtos', label: 'Produtos'},
            {key: 'historico', label: 'Histórico'}
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              style={{
                padding: '12px 4px',
                borderBottom: activeTab === tab.key ? '2px solid #3b82f6' : '2px solid transparent',
                backgroundColor: 'transparent', 
                border: 'none', 
                cursor: 'pointer',
                color: activeTab === tab.key ? '#3b82f6' : '#666', 
                fontSize: '14px',
                fontWeight: activeTab === tab.key ? 'bold' : 'normal'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      <main>
        {activeTab === 'chat' && renderChat()}
        {activeTab === 'produtos' && renderProdutos()}
        {activeTab === 'historico' && renderHistorico()}
      </main>
    </div>
  );
}

export default App;