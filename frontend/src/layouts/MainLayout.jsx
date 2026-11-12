import React from 'react';
import { BrainCircuit, LogIn, UserPlus, LayoutDashboard } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useRouter } from '../router/Router';
import { ROUTES, getDashboardRouteForRole } from '../config/routes';
import './MainLayout.css';

export default function MainLayout({ children }) {
  const { isLoggedIn, currentRole, openAuthModal } = useAuth();
  const { navigate, currentPath } = useRouter();

  const dashboardRoute = getDashboardRouteForRole(currentRole);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: '#080c16', color: '#f8fafc', fontFamily: 'Inter, system-ui, sans-serif' }}>
      
      {/* PUBLIC TOP NAVBAR */}
      <header style={{ background: '#0a0e1a', borderBottom: '1px solid #1e293b', position: 'sticky', top: 0, zIndex: 100 }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '14px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px' }}>
          
          {/* Brand */}
          <div
            onClick={() => navigate(ROUTES.HOME)}
            style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}
          >
            <div style={{
              background: 'linear-gradient(135deg, #4338ca 0%, #6366f1 100%)',
              color: '#fff',
              borderRadius: '12px',
              width: '40px',
              height: '40px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(99,102,241,0.4)'
            }}>
              <BrainCircuit size={22} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '1.2rem', fontWeight: '800', color: '#ffffff' }}>CampusTech AI</span>
                <span style={{ fontSize: '0.68rem', padding: '2px 8px', borderRadius: '999px', background: '#312e81', color: '#a5b4fc', fontWeight: '700' }}>
                  SRIT-ATP
                </span>
              </div>
              <p style={{ margin: 0, fontSize: '0.72rem', color: '#94a3b8' }}>
                Engineering Placement Accelerator • JNTUA Affiliated
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button
              onClick={() => navigate(ROUTES.HOME)}
              style={{
                background: currentPath === ROUTES.HOME ? '#1e293b' : 'transparent',
                border: 'none',
                color: currentPath === ROUTES.HOME ? '#38bdf8' : '#94a3b8',
                padding: '8px 14px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '0.88rem'
              }}
            >
              Home
            </button>

            {isLoggedIn ? (
              <button
                onClick={() => navigate(dashboardRoute)}
                style={{
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  color: '#ffffff',
                  padding: '8px 18px',
                  borderRadius: '8px',
                  border: 'none',
                  cursor: 'pointer',
                  fontWeight: '700',
                  fontSize: '0.88rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <LayoutDashboard size={16} />
                <span>Go to Dashboard</span>
              </button>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => openAuthModal('login')}
                  style={{
                    background: currentPath === ROUTES.LOGIN ? '#3b82f6' : 'rgba(59, 130, 246, 0.12)',
                    border: '1px solid #3b82f6',
                    color: '#ffffff',
                    padding: '8px 16px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: '700',
                    fontSize: '0.88rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                >
                  <LogIn size={16} />
                  <span>Sign In</span>
                </button>

                <button
                  type="button"
                  onClick={() => openAuthModal('register')}
                  style={{
                    background: currentPath === ROUTES.REGISTER ? '#10b981' : 'transparent',
                    border: '1px solid #334155',
                    color: currentPath === ROUTES.REGISTER ? '#ffffff' : '#cbd5e1',
                    padding: '8px 16px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: '600',
                    fontSize: '0.88rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                >
                  <UserPlus size={16} />
                  <span>Register</span>
                </button>
              </>
            )}
          </div>

        </div>
      </header>

      {/* MAIN PUBLIC PAGE CONTENT */}
      <main style={{ flex: 1 }}>
        {children}
      </main>

      {/* FOOTER */}
      <footer style={{ background: '#050811', borderTop: '1px solid #1e293b', color: '#94a3b8', padding: '28px 24px', fontSize: '0.85rem' }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <b>CampusTech AI • AMK Technologies Platform</b>
            <p style={{ margin: '4px 0 0 0', fontSize: '0.78rem', color: '#64748b' }}>
              Tier-2/Tier-3 JNTUA Engineering Placement & AI Learning Ecosystem (SRIT-ATP)
            </p>
          </div>
          <div style={{ display: 'flex', gap: '16px', fontSize: '0.82rem', color: '#94a3b8' }}>
            <span style={{ cursor: 'pointer' }} onClick={() => navigate(ROUTES.HOME)}>Home</span>
            <span>•</span>
            <span style={{ cursor: 'pointer' }} onClick={() => navigate(ROUTES.LOGIN)}>Sign In</span>
            <span>•</span>
            <span style={{ cursor: 'pointer' }} onClick={() => navigate(ROUTES.REGISTER)}>Register</span>
          </div>
        </div>
      </footer>

    </div>
  );
}

