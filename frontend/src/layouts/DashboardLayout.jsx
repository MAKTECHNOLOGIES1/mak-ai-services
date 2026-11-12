import React from 'react';
import {
  Sparkles,
  BarChart3,
  Search,
  FolderGit2,
  BookOpen,
  Award,
  Layers,
  UserCheck,
  Zap,
  LogOut,
  Home,
  Briefcase,
  Terminal,
  Code
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useRouter } from '../router/Router';
import { ROLES_METADATA, ROUTES } from '../config/routes';
import './DashboardLayout.css';

export default function DashboardLayout({ children, activeTab = 'overview', onTabChange }) {
  const { currentUser, currentRole, userPermissions, currentRoleDetails, logout } = useAuth();
  const { navigate } = useRouter();

  const roleMeta = ROLES_METADATA.find(r => r.id === currentRole) || ROLES_METADATA[0];
  const userId = currentUser?.user_id || currentUser?.roll_number || '-';
  const fullName = currentUser?.full_name || currentRoleDetails?.name || 'Authenticated User';
  const tenantId = currentUser?.tenant_id || '-';
  const department = currentUser?.department || '-';

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: '#090d16',
      color: '#f8fafc',
      overflow: 'hidden',
      fontFamily: 'Inter, system-ui, -apple-system, sans-serif'
    }}>
      
      {/* 1. FIXED TOP HEADER BAR (68px) */}
      <header style={{
        height: '68px',
        background: '#0f172a',
        borderBottom: '1px solid #1e293b',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        flexShrink: 0,
        zIndex: 50
      }}>
        {/* Brand & College Tag */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
            color: '#fff',
            borderRadius: '10px',
            padding: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Sparkles size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontWeight: '800', fontSize: '1.1rem', letterSpacing: '-0.02em', color: '#fff' }}>
                AMK Platform
              </span>
              <span style={{
                fontSize: '0.72rem',
                background: 'rgba(56, 189, 248, 0.15)',
                color: '#38bdf8',
                padding: '2px 8px',
                borderRadius: '4px',
                border: '1px solid rgba(56, 189, 248, 0.3)',
                fontWeight: '600'
              }}>
                {tenantId}
              </span>
            </div>
            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
              Srinivasa Ramanujan Institute of Technology (JNTUA Affiliated)
            </div>
          </div>
        </div>

        {/* User Identity & Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          
          {/* Public Home Link */}
          <button
            onClick={() => navigate(ROUTES.HOME)}
            style={{
              background: '#1e293b',
              border: '1px solid #334155',
              color: '#cbd5e1',
              padding: '6px 12px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '0.8rem',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Home size={15} color="#38bdf8" />
            <span>Public Home</span>
          </button>

          {/* Authenticated Role Badge (From Backend) */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: roleMeta.bg,
            border: `1px solid ${roleMeta.border}`,
            padding: '5px 12px',
            borderRadius: '8px',
            color: roleMeta.color,
            fontSize: '0.8rem',
            fontWeight: '700'
          }}>
            <Sparkles size={14} />
            <span>{currentUser?.role_name || roleMeta.badge}</span>
          </div>

          {/* User Profile Badge */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '5px 12px',
            background: '#1e293b',
            borderRadius: '10px',
            border: '1px solid #334155'
          }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: roleMeta.bg,
              border: `1px solid ${roleMeta.border}`,
              color: roleMeta.color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: '700',
              fontSize: '0.85rem'
            }}>
              {fullName.charAt(0)}
            </div>
            <div>
              <div style={{ fontSize: '0.82rem', fontWeight: '700', color: '#f8fafc', lineHeight: 1.2 }}>
                {fullName}
              </div>
              <div style={{ fontSize: '0.72rem', color: roleMeta.color, fontWeight: '600' }}>
                {userId} • {department}
              </div>
            </div>
          </div>

          {/* Sign Out */}
          <button
            onClick={logout}
            title="Sign Out"
            style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#f87171',
              padding: '7px 12px',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.8rem',
              fontWeight: '600'
            }}
          >
            <LogOut size={15} />
            <span>Sign Out</span>
          </button>
        </div>
      </header>

      {/* 2. BODY SPLIT (LEFT FIXED SIDEBAR + RIGHT SCROLLABLE VIEWPORT) */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        
        {/* LEFT FIXED NAVIGATION SIDEBAR (240px) */}
        <aside style={{
          width: '240px',
          background: '#0f172a',
          borderRight: '1px solid #1e293b',
          display: 'flex',
          flexDirection: 'column',
          padding: '20px 14px',
          flexShrink: 0
        }}>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: '#64748b', fontWeight: '700', padding: '0 8px', marginBottom: '10px' }}>
            {roleMeta.badge} Workspace
          </div>

          <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px', flex: 1 }}>
            <button
              onClick={() => onTabChange && onTabChange('overview')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: '10px 12px',
                borderRadius: '8px',
                border: 'none',
                background: activeTab === 'overview' ? roleMeta.bg : 'transparent',
                color: activeTab === 'overview' ? roleMeta.color : '#94a3b8',
                fontSize: '0.88rem',
                fontWeight: activeTab === 'overview' ? '700' : '500',
                cursor: 'pointer',
                textAlign: 'left'
              }}
            >
              <BarChart3 size={18} />
              <span>Dashboard Overview</span>
            </button>

            {currentRole === 'ROLE_STUDENT' && (
              <>
                <button
                  onClick={() => onTabChange && onTabChange('rag')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    border: 'none',
                    background: activeTab === 'rag' ? roleMeta.bg : 'transparent',
                    color: activeTab === 'rag' ? roleMeta.color : '#94a3b8',
                    fontSize: '0.88rem',
                    cursor: 'pointer'
                  }}
                >
                  <Search size={18} />
                  <span>Syllabus RAG AI</span>
                </button>
                <button
                  onClick={() => onTabChange && onTabChange('projects')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    border: 'none',
                    background: activeTab === 'projects' ? roleMeta.bg : 'transparent',
                    color: activeTab === 'projects' ? roleMeta.color : '#94a3b8',
                    fontSize: '0.88rem',
                    cursor: 'pointer'
                  }}
                >
                  <FolderGit2 size={18} />
                  <span>Capstone Projects</span>
                </button>
              </>
            )}

            {(currentRole === 'ROLE_FACULTY' || currentRole === 'ROLE_HOD') && (
              <>
                <button
                  onClick={() => onTabChange && onTabChange('blooms')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    border: 'none',
                    background: activeTab === 'blooms' ? roleMeta.bg : 'transparent',
                    color: activeTab === 'blooms' ? roleMeta.color : '#94a3b8',
                    fontSize: '0.88rem',
                    cursor: 'pointer'
                  }}
                >
                  <BookOpen size={18} />
                  <span>Bloom's AI Exams</span>
                </button>
                <button
                  onClick={() => onTabChange && onTabChange('capstones')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    border: 'none',
                    background: activeTab === 'capstones' ? roleMeta.bg : 'transparent',
                    color: activeTab === 'capstones' ? roleMeta.color : '#94a3b8',
                    fontSize: '0.88rem',
                    cursor: 'pointer'
                  }}
                >
                  <Award size={18} />
                  <span>Capstone Reviews</span>
                </button>
              </>
            )}

            {(currentRole === 'ROLE_ADMIN' || currentRole === 'ROLE_SUPER_ADMIN') && (
              <>
                <button
                  onClick={() => onTabChange && onTabChange('staff')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    border: 'none',
                    background: activeTab === 'staff' ? roleMeta.bg : 'transparent',
                    color: activeTab === 'staff' ? roleMeta.color : '#94a3b8',
                    fontSize: '0.88rem',
                    cursor: 'pointer'
                  }}
                >
                  <UserCheck size={18} />
                  <span>Staff Provisioning</span>
                </button>
                <button
                  onClick={() => onTabChange && onTabChange('roles')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    border: 'none',
                    background: activeTab === 'roles' ? roleMeta.bg : 'transparent',
                    color: activeTab === 'roles' ? roleMeta.color : '#94a3b8',
                    fontSize: '0.88rem',
                    cursor: 'pointer'
                  }}
                >
                  <Layers size={18} />
                  <span>Dynamic Roles</span>
                </button>
              </>
            )}

            {currentRole === 'ROLE_TPO' && (
              <button
                onClick={() => navigate(ROUTES.TPO_DASHBOARD)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  border: 'none',
                  background: 'transparent',
                  color: '#94a3b8',
                  fontSize: '0.88rem',
                  cursor: 'pointer'
                }}
              >
                <Briefcase size={18} />
                <span>Placement Drives</span>
              </button>
            )}

            {currentRole === 'ROLE_TRAINER' && (
              <button
                onClick={() => navigate(ROUTES.TRAINER_DASHBOARD)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  border: 'none',
                  background: 'transparent',
                  color: '#94a3b8',
                  fontSize: '0.88rem',
                  cursor: 'pointer'
                }}
              >
                <Terminal size={18} />
                <span>Technical Labs</span>
              </button>
            )}

            {currentRole === 'ROLE_SR_LEAD' && (
              <button
                onClick={() => navigate(ROUTES.LEAD_DASHBOARD)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  border: 'none',
                  background: 'transparent',
                  color: '#94a3b8',
                  fontSize: '0.88rem',
                  cursor: 'pointer'
                }}
              >
                <Code size={18} />
                <span>Code Reviews & Architecture</span>
              </button>
            )}
          </nav>

          {/* Database Status Telemetry */}
          <div style={{
            background: 'rgba(15, 23, 42, 0.8)',
            border: '1px solid #1e293b',
            borderRadius: '8px',
            padding: '10px',
            fontSize: '0.75rem',
            color: '#64748b'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#10b981', fontWeight: '600', marginBottom: '4px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }}></span>
              <span>Supabase Cloud Pooler</span>
            </div>
            <div>Dept: <b style={{ color: '#94a3b8' }}>{department}</b></div>
            {userPermissions?.length > 0 && (
              <div style={{ fontSize: '0.7rem', color: '#10b981', marginTop: '2px' }}>
                {userPermissions.length} backend permissions active
              </div>
            )}
          </div>
        </aside>

        {/* 3. MAIN SCROLLABLE VIEWPORT (FITS SCREEN WITH SCROLLABLE REGION) */}
        <main style={{
          flex: 1,
          overflowY: 'auto',
          padding: '24px 32px 60px 32px',
          background: '#090d16'
        }}>
          {/* Explicit Scrollable Status Banner Mention */}
          <div style={{
            background: 'linear-gradient(90deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%)',
            border: '1px solid #1e293b',
            borderRadius: '12px',
            padding: '12px 18px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '24px',
            flexWrap: 'wrap',
            gap: '10px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ background: roleMeta.bg, color: roleMeta.color, padding: '6px', borderRadius: '6px' }}>
                <Zap size={16} />
              </div>
              <span style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
                ✨ <b>Active View:</b> <b style={{ color: roleMeta.color }}>{roleMeta.badge}</b> ({window.location.pathname})
              </span>
            </div>
            <span style={{ fontSize: '0.75rem', color: '#64748b', background: '#090d16', padding: '4px 10px', borderRadius: '6px', border: '1px solid #1e293b' }}>
              Viewport: Full Screen • Smooth Scrollable Area Active ↕️
            </span>
          </div>

          {/* DYNAMIC DASHBOARD CONTENT */}
          {children}
        </main>

      </div>

    </div>
  );
}
