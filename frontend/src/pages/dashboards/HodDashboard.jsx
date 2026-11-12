import React, { useState, useEffect } from 'react';
import { RefreshCw, ShieldCheck, Users, BookOpen, BarChart3 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { fetchTenantUsers } from '../../services/authService';
import './DashboardCommon.css';

export default function HodDashboard() {
  const { authToken, currentUser, userPermissions, currentRoleDetails, showToast } = useAuth();

  const [deptUsers, setDeptUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadDeptData = async () => {
    if (!authToken) return;
    setLoading(true);
    try {
      const users = await fetchTenantUsers(authToken, { department: currentUser?.department });
      setDeptUsers(users || []);
    } catch (err) {
      showToast(err?.message || 'Failed to load department users from backend', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDeptData();
  }, [authToken]);

  const studentsCount = deptUsers.filter(u => u.role_id === 'ROLE_STUDENT').length;
  const facultyCount = deptUsers.filter(u => u.role_id === 'ROLE_FACULTY').length;

  return (
    <div>
      {/* Real Department Metrics from Backend */}
      <div className="dash-metrics-grid">
        <div className="dash-metric-card">
          <div className="dash-metric-title">Department Under Review</div>
          <div className="dash-metric-val" style={{ color: '#8b5cf6' }}>{currentUser?.department || '-'}</div>
          <div className="dash-metric-sub" style={{ color: '#94a3b8' }}>Tenant: {currentUser?.tenant_id}</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Registered Department Students</div>
          <div className="dash-metric-val" style={{ color: '#10b981' }}>
            {loading ? '...' : `${studentsCount} Students`}
          </div>
          <div className="dash-metric-sub" style={{ color: '#34d399' }}>Live Supabase identity_service count</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Department Faculty Members</div>
          <div className="dash-metric-val" style={{ color: '#38bdf8' }}>
            {loading ? '...' : `${facultyCount} Faculty`}
          </div>
          <div className="dash-metric-sub" style={{ color: '#94a3b8' }}>Active Provisioned Accounts</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">HOD In-Charge</div>
          <div className="dash-metric-val" style={{ color: '#fff', fontSize: '1.2rem' }}>
            {currentUser?.user_id}
          </div>
          <div className="dash-metric-sub" style={{ color: '#10b981' }}>{currentUser?.full_name}</div>
        </div>
      </div>

      {/* Backend Assigned User Options */}
      <div className="dash-feature-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <div style={{ background: 'rgba(139, 92, 246, 0.1)', color: '#8b5cf6', padding: '8px', borderRadius: '8px' }}>
            <ShieldCheck size={20} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>HOD Governance & Department Powers</h3>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>
              Role: <b>{currentRoleDetails?.name || currentUser?.role_name || 'Head of Department'}</b> • Level {currentRoleDetails?.hierarchy_level || 70}
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px' }}>
          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Users size={18} color="#a78bfa" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Faculty Allocation & Approvals</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Approve course workload and assign academic mentors across sections.</p>
          </div>

          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <BookOpen size={18} color="#38bdf8" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Curriculum & Syllabus Oversight</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Validate alignment with JNTUA autonomous guidelines and NBA criteria.</p>
          </div>

          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <BarChart3 size={18} color="#10b981" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Department Audit Reports</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Aggregate metrics on academic performance, attendance, and placements.</p>
          </div>
        </div>

        {userPermissions.length > 0 && (
          <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid #334155' }}>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: '600' }}>Backend Granted Permissions: </span>
            <div style={{ display: 'inline-flex', gap: '6px', flexWrap: 'wrap', marginLeft: '6px' }}>
              {userPermissions.map((perm) => (
                <span key={perm} style={{ fontSize: '0.72rem', background: '#090d16', color: '#a78bfa', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(139, 92, 246, 0.3)', fontFamily: 'monospace' }}>
                  {perm}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Real Department Users List from Database */}
      <div className="dash-feature-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Department Members Roster</h3>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>Fetched directly from GET /api/v1/users?department={currentUser?.department}</p>
          </div>
          <button
            onClick={loadDeptData}
            style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#1e293b', border: '1px solid #334155', color: '#cbd5e1', padding: '6px 12px', borderRadius: '6px', fontSize: '0.8rem', cursor: 'pointer' }}
          >
            <RefreshCw size={14} /> Refresh Department
          </button>
        </div>

        {loading ? (
          <div style={{ color: '#94a3b8', fontSize: '0.88rem', padding: '20px 0' }}>Loading live department accounts...</div>
        ) : deptUsers.length === 0 ? (
          <div style={{ color: '#64748b', fontSize: '0.88rem' }}>No accounts registered under department {currentUser?.department} yet.</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {deptUsers.map((u) => (
              <div key={u.user_id} className="dash-table-row">
                <div>
                  <b style={{ color: '#fff', fontSize: '0.92rem' }}>{u.full_name}</b>
                  <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                    ID: <span style={{ color: '#38bdf8' }}>{u.user_id}</span> • {u.email}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '0.75rem', background: 'rgba(139, 92, 246, 0.15)', color: '#a78bfa', padding: '3px 8px', borderRadius: '4px', fontWeight: '600' }}>
                    {u.role_name || u.role_id}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: u.is_active ? '#34d399' : '#f87171' }}>
                    {u.is_active ? '● Active' : '● Disabled'}
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
