import React, { useState, useEffect } from 'react';
import { RefreshCw, ShieldCheck, Briefcase, Award, Building } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { fetchTenantUsers } from '../../services/authService';
import './DashboardCommon.css';

export default function TpoDashboard() {
  const { authToken, currentUser, userPermissions, currentRoleDetails, showToast } = useAuth();

  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadCandidates = async () => {
    if (!authToken) return;
    setLoading(true);
    try {
      const list = await fetchTenantUsers(authToken, { role_id: 'ROLE_STUDENT' });
      setCandidates(list || []);
    } catch (err) {
      showToast(err?.message || 'Failed to load candidates from database', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCandidates();
  }, [authToken]);

  return (
    <div>
      {/* Real Placement Metrics from Backend */}
      <div className="dash-metrics-grid">
        <div className="dash-metric-card">
          <div className="dash-metric-title">Registered Student Pool</div>
          <div className="dash-metric-val" style={{ color: '#f59e0b' }}>
            {loading ? '...' : `${candidates.length} Students`}
          </div>
          <div className="dash-metric-sub" style={{ color: '#10b981' }}>Live Supabase identity_service count</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Placement Officer ID</div>
          <div className="dash-metric-val" style={{ fontSize: '1.4rem', color: '#fff' }}>
            {currentUser?.user_id}
          </div>
          <div className="dash-metric-sub" style={{ color: '#94a3b8' }}>{currentUser?.full_name}</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Tenant College</div>
          <div className="dash-metric-val" style={{ color: '#10b981' }}>
            {currentUser?.tenant_id}
          </div>
          <div className="dash-metric-sub" style={{ color: '#38bdf8' }}>Placement Cell Division</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Database Status</div>
          <div className="dash-metric-val" style={{ color: '#34d399', fontSize: '1.3rem' }}>
            Connected
          </div>
          <div className="dash-metric-sub" style={{ color: '#94a3b8' }}>Real-time user telemetry</div>
        </div>
      </div>

      {/* Backend Assigned User Options */}
      <div className="dash-feature-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <div style={{ background: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b', padding: '8px', borderRadius: '8px' }}>
            <ShieldCheck size={20} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>TPO Placement Officer Options</h3>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>
              Role: <b>{currentRoleDetails?.name || currentUser?.role_name || 'Placement Officer'}</b> • Level {currentRoleDetails?.hierarchy_level || 50}
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px' }}>
          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Building size={18} color="#fbbf24" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Corporate Placement Drives</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Schedule campus recruitment drives and track company hiring pipelines.</p>
          </div>

          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Award size={18} color="#38bdf8" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Portfolio Verification</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Audit candidate capstone github repos and verified AI credentials.</p>
          </div>

          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Briefcase size={18} color="#10b981" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Internship Postings</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Post virtual & industry internships matching candidate branches.</p>
          </div>
        </div>

        {userPermissions.length > 0 && (
          <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid #334155' }}>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: '600' }}>Backend Granted Permissions: </span>
            <div style={{ display: 'inline-flex', gap: '6px', flexWrap: 'wrap', marginLeft: '6px' }}>
              {userPermissions.map((perm) => (
                <span key={perm} style={{ fontSize: '0.72rem', background: '#090d16', color: '#fbbf24', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(245, 158, 11, 0.3)', fontFamily: 'monospace' }}>
                  {perm}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Real Candidate Pool from Database */}
      <div className="dash-feature-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Candidate Placement Eligibility Pool</h3>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>Live students query from GET /api/v1/users?role_id=ROLE_STUDENT</p>
          </div>
          <button
            onClick={loadCandidates}
            style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#1e293b', border: '1px solid #334155', color: '#cbd5e1', padding: '6px 12px', borderRadius: '6px', fontSize: '0.8rem', cursor: 'pointer' }}
          >
            <RefreshCw size={14} /> Refresh Candidates
          </button>
        </div>

        {loading ? (
          <div style={{ color: '#94a3b8', fontSize: '0.88rem', padding: '20px 0' }}>Querying student candidates from Supabase...</div>
        ) : candidates.length === 0 ? (
          <div style={{ color: '#64748b', fontSize: '0.88rem' }}>No student records registered in tenant pool yet.</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {candidates.map((c) => (
              <div key={c.user_id} className="dash-table-row">
                <div>
                  <b style={{ color: '#fff', fontSize: '0.92rem' }}>{c.full_name}</b>
                  <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                    Roll No: <span style={{ color: '#38bdf8' }}>{c.user_id}</span> • Dept: {c.department} • Batch: {c.batch_year}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '0.75rem', background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24', padding: '3px 8px', borderRadius: '4px', fontWeight: '600' }}>
                    Eligible Candidate
                  </span>
                  <span style={{ fontSize: '0.75rem', color: c.is_active ? '#34d399' : '#f87171' }}>
                    {c.is_active ? '● Active' : '● Disabled'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
