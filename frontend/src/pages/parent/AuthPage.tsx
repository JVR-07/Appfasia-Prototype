import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/useAuthStore';
import { Logo } from '../../components/Logo';

export const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  
  const login = useAuthStore((state) => state.login);
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Conectar con backend (axios.post('/auth/login'))
    // Simulación de éxito por ahora:
    if (isLogin) {
      login('Tutor Demo', 'uuid-1234');
      navigate('/dashboard');
    } else {
      login(name || 'Nuevo Tutor', 'uuid-5678');
      navigate('/dashboard');
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.logoContainer}>
        <Logo size={80} />
        <h1 style={styles.brandName}>Appfasia</h1>
      </div>
      
      <div className="card" style={styles.card}>
        <div style={styles.tabContainer}>
          <button 
            type="button"
            style={{...styles.tab, ...(isLogin ? styles.activeTab : {})}}
            onClick={() => setIsLogin(true)}
          >
            Iniciar Sesión
          </button>
          <button 
            type="button"
            style={{...styles.tab, ...(!isLogin ? styles.activeTab : {})}}
            onClick={() => setIsLogin(false)}
          >
            Registrarse
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="form-group">
              <label className="form-label">Nombre del Tutor</label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="Ej. María Pérez" 
                value={name}
                onChange={(e) => setName(e.target.value)}
                required={!isLogin}
              />
            </div>
          )}
          
          <div className="form-group">
            <label className="form-label">Correo Electrónico</label>
            <input 
              type="email" 
              className="form-input" 
              placeholder="correo@ejemplo.com" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Contraseña</label>
            <input 
              type="password" 
              className="form-input" 
              placeholder="••••••••" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary" style={styles.submitBtn}>
            {isLogin ? 'Ingresar a mi cuenta' : 'Crear cuenta'}
          </button>
        </form>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    padding: '2rem',
  },
  logoContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    marginBottom: '2rem',
  },
  brandName: {
    marginTop: '1rem',
    color: 'var(--color-primary)',
    fontSize: '2rem',
  },
  card: {
    width: '100%',
    maxWidth: '400px',
  },
  tabContainer: {
    display: 'flex',
    marginBottom: '1.5rem',
    borderBottom: '2px solid #E2E8F0',
  },
  tab: {
    flex: 1,
    padding: '0.75rem',
    background: 'transparent',
    border: 'none',
    borderBottom: '3px solid transparent',
    fontSize: '1rem',
    fontWeight: 600,
    color: 'var(--color-text-muted)',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  activeTab: {
    color: 'var(--color-primary)',
    borderBottomColor: 'var(--color-primary)',
  },
  submitBtn: {
    width: '100%',
    marginTop: '1rem',
  }
};
