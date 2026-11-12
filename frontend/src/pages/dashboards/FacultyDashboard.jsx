import React, { useState, useEffect } from 'react';
import { RefreshCw, FileQuestion, Award, ShieldCheck, Users } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { fetchTenantUsers } from '../../services/authService';
import './DashboardCommon.css';

export default function FacultyDashboard() {
  const { authToken, currentUser, userPermissions, currentRoleDetails, showToast } = useAuth();

  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadStudents = async () => {
    if (!authToken) return;
    setLoading(true);
    try {
      const list = await fetchTenantUsers(authToken, { role_id: 'ROLE_STUDENT', department: currentUser?.department });
      setStudents(list || []);
    } catch (err) {
      showToast(err?.message || 'Failed to fetch student cohort', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStudents();
  }, [authToken]);

  return (
    <div>
      {/* Real Faculty Metrics from Backend */}
      <div className="dash-metrics-grid">
        <div className="dash-metric-card">
          <div className="dash-metric-title">Faculty Member ID</div>
          <div className="dash-metric-val" style={{ color: '#6366f1', fontSize: '1.4rem' }}>
            {currentUser?.user_id}
          </div>
          <div className="dash-metric-sub" style={{ color: '#10b981' }}>{currentUser?.full_name}</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Department Assigned</div>
          <div className="dash-metric-val" style={{ fontSize: '1.4rem' }}>
            {currentUser?.department || '-'}
          </div>
          <div className="dash-metric-sub" style={{ color: '#94a3b8' }}>Tenant: {currentUser?.tenant_id}</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Enrolled Students in Dept</div>
          <div className="dash-metric-val" style={{ color: '#10b981' }}>
            {loading ? '...' : `${students.length} Students`}
          </div>
          <div className="dash-metric-sub" style={{ color: '#34d399' }}>Live identity_service database count</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Account Status</div>
          <div className="dash-metric-val" style={{ color: '#38bdf8', fontSize: '1.3rem' }}>
            {currentUser?.is_active ? 'Active' : 'Disabled'}
          </div>
          <div className="dash-metric-sub" style={{ color: '#10b981' }}>{currentUser?.email}</div>
        </div>
      </div>

      {/* Backend Assigned User Options */}
      <div className="dash-feature-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <div style={{ background: 'rgba(99, 102, 241, 0.1)', color: '#6366f1', padding: '8px', borderRadius: '8px' }}>
            <ShieldCheck size={20} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Faculty Actions & Capabilities</h3>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>
              Role: <b>{currentRoleDetails?.name || currentUser?.role_name || 'Faculty'}</b> • Level {currentRoleDetails?.hierarchy_level || 50}
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px' }}>
          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <FileQuestion size={18} color="#818cf8" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Bloom's Taxonomy Generator</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Generate JNTUA standard mid-term question papers with outcome mapping.</p>
          </div>

          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Award size={18} color="#f59e0b" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Capstone Evaluations</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Review milestone submissions for final year students in {currentUser?.department || 'department'}.</p>
          </div>

          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Users size={18} color="#10b981" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Student Mentorship Roster</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Track individual academic progress and attendance across active cohorts.</p>
          </div>
        </div>

        {userPermissions.length > 0 && (
          <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid #334155' }}>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: '600' }}>Backend Granted Permissions: </span>
            <div style={{ display: 'inline-flex', gap: '6px', flexWrap: 'wrap', marginLeft: '6px' }}>
              {userPermissions.map((perm) => (
                <span key={perm} style={{ fontSize: '0.72rem', background: '#090d16', color: '#818cf8', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(99, 102, 241, 0.3)', fontFamily: 'monospace' }}>
                  {perm}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Real Department Student Cohort from Backend */}
      <div className="dash-feature-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Student Mentorship Cohort ({currentUser?.department})</h3>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>Live student records fetched from GET /api/v1/users</p>
          </div>
          <button
            onClick={loadStudents}
            style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#1e293b', border: '1px solid #334155', color: '#cbd5e1', padding: '6px 12px', borderRadius: '6px', fontSize: '0.8rem', cursor: 'pointer' }}
          >
            <RefreshCw size={14} /> Refresh Cohort
          </button>
        </div>

        {loading ? (
          <div style={{ color: '#94a3b8', fontSize: '0.88rem', padding: '20px 0' }}>Querying students from Supabase database...</div>
        ) : students.length === 0 ? (
          <div style={{ color: '#64748b', fontSize: '0.88rem' }}>No student records registered in department {currentUser?.department} yet.</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {students.map((s) => (
              <div key={s.user_id} className="dash-table-row">
                <div>
                  <b style={{ color: '#fff', fontSize: '0.92rem' }}>{s.full_name}</b>
                  <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                    Roll No: <span style={{ color: '#38bdf8' }}>{s.user_id}</span> • Batch: {s.batch_year} • {s.email}
                  </div>
                </div>
                <span style={{ fontSize: '0.75rem', background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8', padding: '3px 8px', borderRadius: '4px', fontWeight: '600' }}>
                  {s.role_name || 'Student'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
