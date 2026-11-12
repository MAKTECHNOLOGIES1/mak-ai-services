import React, { useState, useEffect } from 'react';
import { RefreshCw, ShieldCheck, Code, GitBranch, Cpu } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { fetchHealthCheck } from '../../services/authService';
import { API_CONFIG } from '../../config/api';
import './DashboardCommon.css';

export default function LeadDashboard() {
  const { currentUser, userPermissions, currentRoleDetails, showToast } = useAuth();

  const [healthStatus, setHealthStatus] = useState(null);
  const [loadingHealth, setLoadingHealth] = useState(false);

  const checkHealth = async () => {
    setLoadingHealth(true);
    try {
      const data = await fetchHealthCheck();
      setHealthStatus(data);
      showToast('Backend health probe succeeded');
    } catch (err) {
      setHealthStatus({ status: 'offline', error: err?.message });
    } finally {
      setLoadingHealth(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  const endpoints = [
    { name: 'Unified Authentication & Login', path: API_CONFIG.ENDPOINTS.AUTH_LOGIN, method: 'POST' },
    { name: 'Student Registration', path: API_CONFIG.ENDPOINTS.AUTH_REGISTER_STUDENT, method: 'POST' },
    { name: 'Admin Staff Provisioning', path: API_CONFIG.ENDPOINTS.AUTH_PROVISION_USER, method: 'POST' },
    { name: 'Dynamic Roles Management', path: API_CONFIG.ENDPOINTS.ROLES, method: 'GET / POST' },
    { name: 'Tenant Users Management', path: API_CONFIG.ENDPOINTS.USERS, method: 'GET / PATCH' },
    { name: 'Current User Profile Token Verification', path: API_CONFIG.ENDPOINTS.AUTH_ME, method: 'GET' }
  ];

  return (
    <div>
      {/* Real Lead Metrics */}
      <div className="dash-metrics-grid">
        <div className="dash-metric-card">
          <div className="dash-metric-title">Lead Architect ID</div>
          <div className="dash-metric-val" style={{ color: '#ec4899', fontSize: '1.4rem' }}>
            {currentUser?.user_id}
          </div>
          <div className="dash-metric-sub" style={{ color: '#10b981' }}>{currentUser?.full_name}</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Active Environment Base URL</div>
          <div className="dash-metric-val" style={{ fontSize: '0.95rem', color: '#38bdf8', wordBreak: 'break-all' }}>
            {API_CONFIG.GATEWAY_URL}
          </div>
          <div className="dash-metric-sub" style={{ color: '#94a3b8' }}>Cloudflare Edge Worker Domain</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Backend Service Health</div>
          <div className="dash-metric-val" style={{ color: healthStatus?.status === 'offline' ? '#f87171' : '#10b981', fontSize: '1.4rem' }}>
            {loadingHealth ? 'Checking...' : healthStatus?.status || 'Online'}
          </div>
          <div className="dash-metric-sub" style={{ color: '#34d399' }}>Live probe via GET /health</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Tenant Realm</div>
          <div className="dash-metric-val" style={{ color: '#8b5cf6' }}>
            {currentUser?.tenant_id}
          </div>
          <div className="dash-metric-sub" style={{ color: '#38bdf8' }}>schema: identity_service</div>
        </div>
      </div>

      {/* Backend Assigned User Options */}
      <div className="dash-feature-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <div style={{ background: 'rgba(236, 72, 153, 0.1)', color: '#ec4899', padding: '8px', borderRadius: '8px' }}>
            <ShieldCheck size={20} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Senior Technical Lead Controls</h3>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>
              Role: <b>{currentRoleDetails?.name || currentUser?.role_name || 'Senior Technical Lead'}</b> • Level {currentRoleDetails?.hierarchy_level || 65}
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px' }}>
          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Code size={18} color="#f472b6" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Automated Code Reviews</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Run static analysis and test coverage verification against student git PRs.</p>
          </div>

          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <GitBranch size={18} color="#38bdf8" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Architecture Verification</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Verify microservice boundaries, clean code standards, and database isolation.</p>
          </div>

          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Cpu size={18} color="#34d399" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Edge Gateway Telemetry</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Inspect Cloudflare Workers latency, rate limits, and cross-origin headers.</p>
          </div>
        </div>

        {userPermissions.length > 0 && (
          <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid #334155' }}>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: '600' }}>Backend Granted Permissions: </span>
            <div style={{ display: 'inline-flex', gap: '6px', flexWrap: 'wrap', marginLeft: '6px' }}>
              {userPermissions.map((perm) => (
                <span key={perm} style={{ fontSize: '0.72rem', background: '#090d16', color: '#f472b6', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(236, 72, 153, 0.3)', fontFamily: 'monospace' }}>
                  {perm}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Backend API Endpoints Matrix */}
      <div className="dash-feature-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Centralized Backend Endpoints Roster</h3>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>Strictly zero localhost URLs. Live routes consumed by the UI</p>
          </div>
          <button
            onClick={checkHealth}
            style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#1e293b', border: '1px solid #334155', color: '#cbd5e1', padding: '6px 12px', borderRadius: '6px', fontSize: '0.8rem', cursor: 'pointer' }}
          >
            <RefreshCw size={14} /> Probe API
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {endpoints.map((ep) => (
            <div key={ep.name} className="dash-table-row">
              <div>
                <b style={{ color: '#fff', fontSize: '0.92rem' }}>{ep.name}</b>
                <div style={{ fontSize: '0.78rem', color: '#38bdf8', fontFamily: 'monospace' }}>
                  {API_CONFIG.GATEWAY_URL}{ep.path}
                </div>
              </div>
              <span style={{ fontSize: '0.72rem', background: '#090d16', color: '#a78bfa', padding: '3px 8px', borderRadius: '4px', border: '1px solid #334155', fontWeight: '600' }}>
                {ep.method}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
