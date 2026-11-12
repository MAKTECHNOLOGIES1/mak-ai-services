import React, { useState, useEffect } from 'react';
import { RefreshCw, ShieldCheck, Terminal, Award, CheckSquare } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { fetchTenantUsers } from '../../services/authService';
import './DashboardCommon.css';

export default function TrainerDashboard() {
  const { authToken, currentUser, userPermissions, currentRoleDetails, showToast } = useAuth();

  const [trainees, setTrainees] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadTrainees = async () => {
    if (!authToken) return;
    setLoading(true);
    try {
      const list = await fetchTenantUsers(authToken, { role_id: 'ROLE_STUDENT' });
      setTrainees(list || []);
    } catch (err) {
      showToast(err?.message || 'Failed to fetch trainee pool', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTrainees();
  }, [authToken]);

  return (
    <div>
      {/* Real Trainer Metrics */}
      <div className="dash-metrics-grid">
        <div className="dash-metric-card">
          <div className="dash-metric-title">Enrolled Trainee Pool</div>
          <div className="dash-metric-val" style={{ color: '#06b6d4' }}>
            {loading ? '...' : `${trainees.length} Students`}
          </div>
          <div className="dash-metric-sub" style={{ color: '#10b981' }}>Live Supabase identity_service count</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Trainer ID</div>
          <div className="dash-metric-val" style={{ color: '#fff', fontSize: '1.4rem' }}>
            {currentUser?.user_id}
          </div>
          <div className="dash-metric-sub" style={{ color: '#94a3b8' }}>{currentUser?.full_name}</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Department Specialization</div>
          <div className="dash-metric-val" style={{ color: '#10b981' }}>
            {currentUser?.department || '-'}
          </div>
          <div className="dash-metric-sub" style={{ color: '#38bdf8' }}>Tenant: {currentUser?.tenant_id}</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Trainer Role Status</div>
          <div className="dash-metric-val" style={{ color: currentUser?.is_active ? '#34d399' : '#f87171', fontSize: '1.3rem' }}>
            {currentUser?.is_active ? 'Active' : 'Disabled'}
          </div>
          <div className="dash-metric-sub" style={{ color: '#94a3b8' }}>Technical Lab Instructor</div>
        </div>
      </div>

      {/* Backend Assigned User Options */}
      <div className="dash-feature-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <div style={{ background: 'rgba(6, 182, 212, 0.1)', color: '#06b6d4', padding: '8px', borderRadius: '8px' }}>
            <ShieldCheck size={20} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Trainer Lab & Curriculum Actions</h3>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>
              Role: <b>{currentRoleDetails?.name || currentUser?.role_name || 'Technical Trainer'}</b> • Level {currentRoleDetails?.hierarchy_level || 60}
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px' }}>
          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Terminal size={18} color="#22d3ee" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Hands-On Coding Labs</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Deploy programming test benches and review student code execution.</p>
          </div>

          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Award size={18} color="#38bdf8" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Assessment Grading</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Grade student submissions against JNTUA evaluation rubrics.</p>
          </div>

          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <CheckSquare size={18} color="#10b981" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Workshop Attendance</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Log live session attendance and technical lab participation.</p>
          </div>
        </div>

        {userPermissions.length > 0 && (
          <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid #334155' }}>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: '600' }}>Backend Granted Permissions: </span>
            <div style={{ display: 'inline-flex', gap: '6px', flexWrap: 'wrap', marginLeft: '6px' }}>
              {userPermissions.map((perm) => (
                <span key={perm} style={{ fontSize: '0.72rem', background: '#090d16', color: '#22d3ee', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(6, 182, 212, 0.3)', fontFamily: 'monospace' }}>
                  {perm}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Trainees List from Database */}
      <div className="dash-feature-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Technical Training Trainees Roster</h3>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>Live students query from GET /api/v1/users?role_id=ROLE_STUDENT</p>
          </div>
          <button
            onClick={loadTrainees}
            style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#1e293b', border: '1px solid #334155', color: '#cbd5e1', padding: '6px 12px', borderRadius: '6px', fontSize: '0.8rem', cursor: 'pointer' }}
          >
            <RefreshCw size={14} /> Refresh Roster
          </button>
        </div>

        {loading ? (
          <div style={{ color: '#94a3b8', fontSize: '0.88rem', padding: '20px 0' }}>Querying students from database...</div>
        ) : trainees.length === 0 ? (
          <div style={{ color: '#64748b', fontSize: '0.88rem' }}>No trainees currently registered in tenant pool.</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {trainees.map((t) => (
              <div key={t.user_id} className="dash-table-row">
                <div>
                  <b style={{ color: '#fff', fontSize: '0.92rem' }}>{t.full_name}</b>
                  <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                    Roll No: <span style={{ color: '#38bdf8' }}>{t.user_id}</span> • Dept: {t.department} • Batch: {t.batch_year}
                  </div>
                </div>
                <span style={{ fontSize: '0.75rem', background: 'rgba(6, 182, 212, 0.15)', color: '#22d3ee', padding: '3px 8px', borderRadius: '4px', fontWeight: '600' }}>
                  {t.role_name || 'Student'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
