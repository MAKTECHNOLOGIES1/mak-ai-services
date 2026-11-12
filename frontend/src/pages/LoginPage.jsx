import React, { useState } from 'react';
import {
  ShieldCheck,
  User,
  Lock,
  Eye,
  EyeOff,
  LogIn
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Link } from '../router/Router';
import { ROUTES } from '../config/routes';
import './AuthPages.css';

export default function LoginPage() {
  const { login } = useAuth();

  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!identifier.trim() || !password) {
      setError('Please provide your Roll Number, Staff ID, or Email and password.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await login(identifier.trim(), password);
    } catch (err) {
      setError(err?.message || 'Login failed. Please verify your credentials against the backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '480px', margin: '40px auto 60px auto', padding: '0 20px' }}>
      
      {/* CARD CONTAINER */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%)',
        border: '1px solid rgba(56, 189, 248, 0.25)',
        borderRadius: '20px',
        padding: '36px',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.6)'
      }}>
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '52px',
            height: '52px',
            borderRadius: '14px',
            background: 'rgba(56, 189, 248, 0.15)',
            color: '#38bdf8',
            marginBottom: '12px'
          }}>
            <ShieldCheck size={28} />
          </div>
          <h2 style={{ fontSize: '1.7rem', fontWeight: '800', margin: '0 0 6px 0', color: '#ffffff' }}>
            Sign In to AMK Platform
          </h2>
          <p style={{ margin: 0, fontSize: '0.88rem', color: '#94a3b8' }}>
            Enter your credentials. Your role and workspace will be detected automatically.
          </p>
        </div>

        {/* Global Unified Login Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', color: '#94a3b8', fontWeight: '600', marginBottom: '6px' }}>
              Roll Number / Staff ID / Email
            </label>
            <div style={{ position: 'relative' }}>
              <User size={18} color="#64748b" style={{ position: 'absolute', left: '12px', top: '13px' }} />
              <input
                type="text"
                required
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="e.g. 22731A0501 or ADM-SRIT-001"
                style={{
                  width: '100%',
                  padding: '12px 14px 12px 40px',
                  background: '#090d16',
                  border: '1px solid #334155',
                  borderRadius: '10px',
                  color: '#ffffff',
                  fontSize: '0.92rem',
                  boxSizing: 'border-box'
                }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', color: '#94a3b8', fontWeight: '600', marginBottom: '6px' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={18} color="#64748b" style={{ position: 'absolute', left: '12px', top: '13px' }} />
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                style={{
                  width: '100%',
                  padding: '12px 42px 12px 40px',
                  background: '#090d16',
                  border: '1px solid #334155',
                  borderRadius: '10px',
                  color: '#ffffff',
                  fontSize: '0.92rem',
                  boxSizing: 'border-box'
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '12px',
                  top: '12px',
                  background: 'none',
                  border: 'none',
                  color: '#64748b',
                  cursor: 'pointer',
                  padding: 0
                }}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          {error && (
            <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', padding: '10px 14px', color: '#f87171', fontSize: '0.82rem' }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
              color: '#ffffff',
              padding: '13px',
              borderRadius: '10px',
              border: 'none',
              fontSize: '0.95rem',
              fontWeight: '700',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              boxShadow: '0 4px 14px rgba(37, 99, 235, 0.4)',
              marginTop: '6px'
            }}
          >
            <LogIn size={18} />
            <span>{loading ? 'Authenticating...' : 'Sign In & Launch Dashboard'}</span>
          </button>
        </form>

        {/* Footer Navigation */}
        <div style={{ borderTop: '1px solid #1e293b', marginTop: '24px', paddingTop: '18px', textAlign: 'center', fontSize: '0.82rem', color: '#94a3b8' }}>
          Don't have an account?{' '}
          <Link to={ROUTES.REGISTER} style={{ color: '#38bdf8', fontWeight: '600', textDecoration: 'none' }}>
            Register as a Student &rarr;
          </Link>
        </div>

      </div>

    </div>
  );
}
