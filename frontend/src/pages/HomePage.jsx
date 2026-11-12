import React from 'react';
import {
  Sparkles,
  ArrowRight,
  LogIn,
  UserPlus,
  BrainCircuit,
  Award,
  ShieldCheck
} from 'lucide-react';
import { useRouter } from '../router/Router';
import { useAuth } from '../context/AuthContext';
import { ROLES_METADATA, getDashboardRouteForRole } from '../config/routes';
import './HomePage.css';

export default function HomePage() {
  const { navigate } = useRouter();
  const { isLoggedIn, currentRole, openAuthModal } = useAuth();

  const dashboardRoute = getDashboardRouteForRole(currentRole);

  return (
    <div style={{ background: '#080c16', color: '#f8fafc' }}>
      
      {/* 1. HERO SECTION */}
      <section style={{
        position: 'relative',
        overflow: 'hidden',
        padding: '70px 24px 60px 24px',
        background: 'radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.22) 0%, rgba(8, 12, 22, 0) 70%)',
        borderBottom: '1px solid rgba(255,255,255,0.06)'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', textAlign: 'center' }}>
          
          {/* Eyebrow Pill */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: 'rgba(99, 102, 241, 0.12)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            padding: '6px 18px',
            borderRadius: '999px',
            fontSize: '0.85rem',
            fontWeight: '700',
            color: '#a5b4fc',
            marginBottom: '20px'
          }}>
            <Sparkles size={16} color="#fbbf24" />
            <span>Campus Career & Institutional Acceleration • SRIT-ATP</span>
          </div>

          {/* Hero Headline */}
          <h1 style={{
            fontSize: 'clamp(2.3rem, 5vw, 3.8rem)',
            fontWeight: '900',
            letterSpacing: '-1.5px',
            lineHeight: 1.15,
            margin: '0 auto 18px auto',
            maxWidth: '960px',
            background: 'linear-gradient(180deg, #ffffff 0%, #cbd5e1 70%, #94a3b8 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            AI-First College Transformation Platform for Tier-2/Tier-3 Engineering
          </h1>

          {/* Subtitle */}
          <p style={{
            fontSize: 'clamp(1rem, 2vw, 1.25rem)',
            color: '#94a3b8',
            maxWidth: '780px',
            margin: '0 auto 34px auto',
            lineHeight: 1.6
          }}>
            Empowering students, faculty, HODs, and placement officers with role-based intelligent dashboards, 
            hands-on virtual internships, AI mock interviews, and automated Bloom's taxonomy exams.
          </p>

          {/* Action CTAs */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', flexWrap: 'wrap', marginBottom: '40px' }}>
            {isLoggedIn ? (
              <button
                onClick={() => navigate(dashboardRoute)}
                style={{
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  color: '#ffffff',
                  padding: '14px 32px',
                  borderRadius: '12px',
                  fontSize: '1rem',
                  fontWeight: '700',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  boxShadow: '0 10px 25px -5px rgba(16, 185, 129, 0.4)'
                }}
              >
                <span>Enter Role Dashboard ({currentRole.replace('ROLE_', '')})</span>
                <ArrowRight size={18} />
              </button>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => openAuthModal('login')}
                  style={{
                    background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
                    color: '#ffffff',
                    padding: '14px 30px',
                    borderRadius: '12px',
                    fontSize: '1rem',
                    fontWeight: '700',
                    border: 'none',
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '8px',
                    boxShadow: '0 10px 25px -5px rgba(37, 99, 235, 0.4)'
                  }}
                >
                  <LogIn size={18} />
                  <span>Sign In</span>
                </button>

                <button
                  type="button"
                  onClick={() => openAuthModal('register')}
                  style={{
                    background: 'transparent',
                    color: '#38bdf8',
                    padding: '14px 26px',
                    borderRadius: '12px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    border: '1px solid rgba(56, 189, 248, 0.4)',
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <UserPlus size={18} />
                  <span>Student Register</span>
                </button>
              </>
            )}
          </div>

          {/* Supported Institutional Roles Preview */}
          <div style={{
            maxWidth: '920px',
            margin: '0 auto',
            background: 'rgba(15, 23, 42, 0.85)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '16px',
            padding: '24px',
            textAlign: 'left'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px', color: '#94a3b8', fontSize: '0.82rem', fontWeight: '600' }}>
              <ShieldCheck size={16} color="#38bdf8" />
              <span>Supported Institutional Roles & Workspaces (Automatically Routed on Login):</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
              {ROLES_METADATA.map((r) => (
                <div
                  key={r.id}
                  onClick={() => openAuthModal('login')}
                  style={{
                    background: '#090d16',
                    border: '1px solid #334155',
                    borderRadius: '10px',
                    padding: '12px 14px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer'
                  }}
                  title={`Sign in to access ${r.badge} workspace`}
                >
                  <div>
                    <div style={{ color: r.color, fontWeight: '700', fontSize: '0.88rem' }}>{r.badge}</div>
                    <div style={{ color: '#64748b', fontSize: '0.72rem' }}>{r.path}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </section>

      {/* 2. THREE KEY PILLARS */}
      <section style={{ padding: '60px 24px', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '22px' }}>
          
          <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '16px', padding: '26px' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
              <ShieldCheck size={22} />
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#ffffff', margin: '0 0 10px 0' }}>
              Role-Based Institutional Portals
            </h3>
            <p style={{ color: '#94a3b8', fontSize: '0.88rem', lineHeight: 1.6, margin: 0 }}>
              Tailored workspaces for Students, Faculty, HODs, TPO, Admins, and Tech Leads with granular permissions.
            </p>
          </div>

          <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '16px', padding: '26px' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: 'rgba(168, 85, 247, 0.1)', color: '#a855f7', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
              <BrainCircuit size={22} />
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#ffffff', margin: '0 0 10px 0' }}>
              Syllabus & Regulation RAG AI
            </h3>
            <p style={{ color: '#94a3b8', fontSize: '0.88rem', lineHeight: 1.6, margin: 0 }}>
              Vector embeddings over JNTUA R20 academic regulations and course outcomes powered by Supabase PostgreSQL.
            </p>
          </div>

          <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '16px', padding: '26px' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
              <Award size={22} />
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#ffffff', margin: '0 0 10px 0' }}>
              Placement & CRT Tracking
            </h3>
            <p style={{ color: '#94a3b8', fontSize: '0.88rem', lineHeight: 1.6, margin: 0 }}>
              Real-time student eligibility pools, company drive notifications, and placement conversion metrics for TPOs.
            </p>
          </div>

        </div>
      </section>

    </div>
  );
}
