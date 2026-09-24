// src/Login.jsx
import { useState } from 'react';

export default function Login({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Credenciales inválidas');
      }
      
      const data = await response.json();
      
      // Enviamos el usuario autenticado (id, username, rol)
      onLoginSuccess(data.usuario);
      
    } catch (err) {
      setError(err.message || 'Usuario o contraseña incorrectos');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ height: '100vh', width: '100vw', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#0f172a', fontFamily: 'system-ui', boxSizing: 'border-box' }}>
      <div style={{ backgroundColor: '#1e293b', padding: '40px', borderRadius: '16px', border: '1px solid #334155', width: '100%', maxWidth: '400px', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.5)', boxSizing: 'border-box' }}>
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <div style={{ width: '60px', height: '60px', backgroundColor: '#38bdf8', borderRadius: '50%', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '30px', margin: '0 auto 15px auto', color: '#0f172a', fontWeight: 'bold' }}>+</div>
          <h2 style={{ color: '#f8fafc', margin: 0 }}>HOSPITAL SAN JOSÉ</h2>
          <p style={{ color: '#94a3b8', margin: '5px 0 0 0', fontSize: '14px' }}>Acceso al Centro de Mando</p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <label style={{ display: 'block', color: '#cbd5e1', fontSize: '13px', marginBottom: '8px' }}>Usuario</label>
            <input 
              type="text" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)} 
              required 
              style={{ width: '100%', padding: '12px', backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc', outline: 'none', boxSizing: 'border-box' }} 
              placeholder="Ej: medico o admin" 
            />
          </div>
          <div>
            <label style={{ display: 'block', color: '#cbd5e1', fontSize: '13px', marginBottom: '8px' }}>Contraseña</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required 
              style={{ width: '100%', padding: '12px', backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc', outline: 'none', boxSizing: 'border-box' }} 
              placeholder="••••••••" 
            />
          </div>

          {error && <div style={{ color: '#ef4444', fontSize: '13px', textAlign: 'center', backgroundColor: 'rgba(239,68,68,0.1)', padding: '10px', borderRadius: '6px' }}>{error}</div>}

          <button type="submit" disabled={loading} style={{ width: '100%', padding: '12px', backgroundColor: '#38bdf8', color: '#0f172a', border: 'none', borderRadius: '8px', fontWeight: 'bold', fontSize: '15px', cursor: 'pointer', marginTop: '10px' }}>
            {loading ? 'Verificando...' : 'Ingresar al Sistema'}
          </button>
        </form>
      </div>
    </div>
  );
}