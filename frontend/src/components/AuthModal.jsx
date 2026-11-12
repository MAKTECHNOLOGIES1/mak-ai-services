import React, { useState, useEffect } from 'react';
import {
  X,
  ShieldCheck,
  User,
  Lock,
  Eye,
  EyeOff,
  LogIn,
  UserPlus,
  GraduationCap,
  Mail,
  Building2
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import './AuthModal.css';

export default function AuthModal({ isOpen, initialTab = 'login', onClose }) {
  const { login, register } = useAuth();

  const [activeTab, setActiveTab] = useState(initialTab);

  // Login form state
  const [loginIdentifier, setLoginIdentifier] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState('');

  // Register form state
  const [regForm, setRegForm] = useState({
    roll_number: '',
    email: '',
    full_name: '',
    password: '',
    department: 'CSE',
    batch_year: '',
    tenant_id: 'SRIT-ATP'
  });
  const [showRegPassword, setShowRegPassword] = useState(false);
  const [regLoading, setRegLoading] = useState(false);
  const [regError, setRegError] = useState('');

  // Synchronize initialTab when modal opens
  useEffect(() => {
    if (isOpen) {
      setActiveTab(initialTab);
      setLoginError('');
      setRegError('');
    }
  }, [isOpen, initialTab]);

  // Close on Escape key press
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  // Handle Login submission
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    if (!loginIdentifier.trim() || !loginPassword) {
      setLoginError('Please provide your Roll Number, Staff ID, or Email and password.');
      return;
    }

    setLoginLoading(true);
    setLoginError('');

    try {
      await login(loginIdentifier.trim(), loginPassword);
      onClose();
    } catch (err) {
      setLoginError(err?.message || 'Login failed. Please verify your credentials.');
    } finally {
      setLoginLoading(false);
    }
  };

  // Handle Student Registration submission
  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    if (!regForm.roll_number.trim() || !regForm.email.trim() || !regForm.full_name.trim() || !regForm.password) {
      setRegError('Please fill in all required registration fields.');
      return;
    }

    setRegLoading(true);
    setRegError('');

    try {
      await register(regForm);
      onClose();
    } catch (err) {
      setRegError(err?.message || 'Registration failed. Please check your information.');
    } finally {
      setRegLoading(false);
    }
  };

  return (
    <div
      className="auth-modal-overlay"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="auth-modal-container" role="dialog" aria-modal="true">
        
        {/* Close button */}
        <button
          onClick={onClose}
          className="auth-modal-close-btn"
          title="Close dialog (Esc)"
          aria-label="Close"
        >
          <X size={18} />
        </button>

        {/* Tab switcher: Sign In vs Student Register */}
        <div className="auth-modal-tabs">
          <button
            type="button"
            onClick={() => {
              setActiveTab('login');
              setLoginError('');
            }}
            className={`auth-modal-tab ${activeTab === 'login' ? 'active login' : ''}`}
          >
            <LogIn size={15} />
            <span>Sign In</span>
          </button>
          <button
            type="button"
            onClick={() => {
              setActiveTab('register');
              setRegError('');
            }}
            className={`auth-modal-tab ${activeTab === 'register' ? 'active register' : ''}`}
          >
            <UserPlus size={15} />
            <span>Student Register</span>
          </button>
        </div>

        {/* 1. SIGN IN TAB */}
        {activeTab === 'login' && (
          <div>
            <div className="auth-modal-header">
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '46px',
                height: '46px',
                borderRadius: '12px',
                background: 'rgba(56, 189, 248, 0.15)',
                color: '#38bdf8',
                marginBottom: '10px'
              }}>
                <ShieldCheck size={24} />
              </div>
              <h2 className="auth-modal-title">Sign In to AMK Platform</h2>
              <p className="auth-modal-sub">
                Enter your credentials. Your role and workspace will be detected automatically.
              </p>
            </div>

            <form onSubmit={handleLoginSubmit} className="auth-modal-form">
              <div>
                <label className="auth-modal-label">Roll Number / Staff ID / Email</label>
                <div className="auth-modal-input-wrap">
                  <User size={18} color="#64748b" style={{ position: 'absolute', left: '12px', top: '12px' }} />
                  <input
                    type="text"
                    required
                    value={loginIdentifier}
                    onChange={(e) => setLoginIdentifier(e.target.value)}
                    placeholder="e.g. 22731A0501 or ADM-SRIT-001"
                    className="auth-modal-input"
                    autoFocus
                  />
                </div>
              </div>

              <div>
                <label className="auth-modal-label">Password</label>
                <div className="auth-modal-input-wrap">
                  <Lock size={18} color="#64748b" style={{ position: 'absolute', left: '12px', top: '12px' }} />
                  <input
                    type={showLoginPassword ? 'text' : 'password'}
                    required
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="••••••••"
                    className="auth-modal-input has-right"
                  />
                  <button
                    type="button"
                    onClick={() => setShowLoginPassword(!showLoginPassword)}
                    className="auth-modal-eye-btn"
                  >
                    {showLoginPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              {loginError && (
                <div className="auth-modal-error">
                  {loginError}
                </div>
              )}

              <button
                type="submit"
                disabled={loginLoading}
                className="auth-modal-submit login-btn"
              >
                <LogIn size={18} />
                <span>{loginLoading ? 'Authenticating...' : 'Sign In & Launch Dashboard'}</span>
              </button>
            </form>

            <div className="auth-modal-footer">
              Don't have an account?{' '}
              <button
                type="button"
                onClick={() => setActiveTab('register')}
                className="auth-modal-switch-btn"
              >
                Register as a Student &rarr;
              </button>
            </div>
          </div>
        )}

        {/* 2. STUDENT REGISTER TAB */}
        {activeTab === 'register' && (
          <div>
            <div className="auth-modal-header">
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '46px',
                height: '46px',
                borderRadius: '12px',
                background: 'rgba(16, 185, 129, 0.15)',
                color: '#10b981',
                marginBottom: '10px'
              }}>
                <GraduationCap size={24} />
              </div>
              <h2 className="auth-modal-title">Student Registration</h2>
              <p className="auth-modal-sub">
                Create your student record on AMK Platform (SRIT-ATP • JNTUA Affiliated)
              </p>
            </div>

            <form onSubmit={handleRegisterSubmit} className="auth-modal-form">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label className="auth-modal-label">Student Roll Number</label>
                  <div className="auth-modal-input-wrap">
                    <User size={16} color="#64748b" style={{ position: 'absolute', left: '12px', top: '12px' }} />
                    <input
                      type="text"
                      required
                      value={regForm.roll_number}
                      onChange={(e) => setRegForm({ ...regForm, roll_number: e.target.value })}
                      placeholder="e.g. 22731A0501"
                      className="auth-modal-input"
                    />
                  </div>
                </div>

                <div>
                  <label className="auth-modal-label">Full Name</label>
                  <div className="auth-modal-input-wrap">
                    <input
                      type="text"
                      required
                      value={regForm.full_name}
                      onChange={(e) => setRegForm({ ...regForm, full_name: e.target.value })}
                      placeholder="Full Name"
                      className="auth-modal-input"
                      style={{ paddingLeft: '14px' }}
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="auth-modal-label">College Email</label>
                <div className="auth-modal-input-wrap">
                  <Mail size={16} color="#64748b" style={{ position: 'absolute', left: '12px', top: '12px' }} />
                  <input
                    type="email"
                    required
                    value={regForm.email}
                    onChange={(e) => setRegForm({ ...regForm, email: e.target.value })}
                    placeholder="student@srit.ac.in"
                    className="auth-modal-input"
                  />
                </div>
              </div>

              <div>
                <label className="auth-modal-label">Password</label>
                <div className="auth-modal-input-wrap">
                  <Lock size={16} color="#64748b" style={{ position: 'absolute', left: '12px', top: '12px' }} />
                  <input
                    type={showRegPassword ? 'text' : 'password'}
                    required
                    value={regForm.password}
                    onChange={(e) => setRegForm({ ...regForm, password: e.target.value })}
                    placeholder="Minimum 8 characters"
                    className="auth-modal-input has-right"
                  />
                  <button
                    type="button"
                    onClick={() => setShowRegPassword(!showRegPassword)}
                    className="auth-modal-eye-btn"
                  >
                    {showRegPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label className="auth-modal-label">Department</label>
                  <div className="auth-modal-input-wrap">
                    <Building2 size={16} color="#64748b" style={{ position: 'absolute', left: '12px', top: '12px' }} />
                    <select
                      value={regForm.department}
                      onChange={(e) => setRegForm({ ...regForm, department: e.target.value })}
                      className="auth-modal-input"
                      style={{ paddingLeft: '38px', background: '#090d16' }}
                    >
                      <option value="CSE">CSE</option>
                      <option value="ECE">ECE</option>
                      <option value="EEE">EEE</option>
                      <option value="MECH">MECH</option>
                      <option value="CIVIL">CIVIL</option>
                      <option value="AI_DS">AI & DS</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="auth-modal-label">Academic Batch</label>
                  <div className="auth-modal-input-wrap">
                    <input
                      type="text"
                      value={regForm.batch_year}
                      onChange={(e) => setRegForm({ ...regForm, batch_year: e.target.value })}
                      placeholder="e.g. 2022-2026"
                      className="auth-modal-input"
                      style={{ paddingLeft: '14px' }}
                    />
                  </div>
                </div>
              </div>

              {regError && (
                <div className="auth-modal-error">
                  {regError}
                </div>
              )}

              <button
                type="submit"
                disabled={regLoading}
                className="auth-modal-submit register-btn"
              >
                <UserPlus size={18} />
                <span>{regLoading ? 'Registering...' : 'Complete Registration & Launch'}</span>
              </button>
            </form>

            <div className="auth-modal-footer">
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => setActiveTab('login')}
                className="auth-modal-switch-btn"
              >
                Sign In Instead &rarr;
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

