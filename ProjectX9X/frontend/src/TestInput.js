import React, { useState } from 'react';

function TestInput() {
  const [texto, setTexto] = useState('');

  return (
    <div style={{padding: '20px'}}>
      <h2>Teste de Input</h2>
      <input
        type="text"
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        placeholder="Digite aqui para testar..."
        style={{
          width: '300px',
          padding: '10px',
          fontSize: '16px',
          border: '1px solid #ccc'
        }}
      />
      <p>Você digitou: {texto}</p>
    </div>
  );
}

export default TestInput;