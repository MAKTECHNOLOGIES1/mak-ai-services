import React, { useState, useEffect } from 'react';
import { UserCheck, RefreshCw, ShieldCheck, Layers, Settings, FileSpreadsheet } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { provisionStaff, fetchRoles, fetchTenantUsers, toggleUserStatus } from '../../services/authService';
import './DashboardCommon.css';

export default function AdminDashboard() {
  const { authToken, currentUser, userPermissions, currentRoleDetails, showToast } = useAuth();

  const [roles, setRoles] = useState([]);
  const [users, setUsers] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [loadingRoles, setLoadingRoles] = useState(false);

  const [staffForm, setStaffForm] = useState({
    staff_id: '',
    email: '',
    full_name: '',
    initial_password: '',
    role_id: 'ROLE_FACULTY',
    department: 'CSE'
  });

  const [provisioning, setProvisioning] = useState(false);
  const [provisionError, setProvisionError] = useState('');

  // Fetch real roles and tenant users from backend
  const loadBackendData = async () => {
    if (!authToken) return;
    setLoadingUsers(true);
    setLoadingRoles(true);

    try {
      const rolesList = await fetchRoles();
      setRoles(rolesList || []);
    } catch (err) {
      console.warn('Could not load roles:', err?.message);
    } finally {
      setLoadingRoles(false);
    }

    try {
      const usersList = await fetchTenantUsers(authToken);
      setUsers(usersList || []);
    } catch (err) {
      console.warn('Could not load tenant users:', err?.message);
    } finally {
      setLoadingUsers(false);
    }
  };

  useEffect(() => {
    loadBackendData();
  }, [authToken]);

  const handleProvisionSubmit = async (e) => {
    e.preventDefault();
    setProvisioning(true);
    setProvisionError('');

    try {
      await provisionStaff(staffForm, authToken);
      showToast(`Account provisioned successfully for ${staffForm.full_name} (${staffForm.role_id})`);
      setStaffForm({
        staff_id: '',
        email: '',
        full_name: '',
        initial_password: 'Password123!',
        role_id: 'ROLE_FACULTY',
        department: 'CSE'
      });
      // Refresh real users list from backend
      await loadBackendData();
    } catch (err) {
      setProvisionError(err?.message || 'Provisioning failed on backend.');
      showToast(err?.message || 'Provisioning failed', 'error');
    } finally {
      setProvisioning(false);
    }
  };

  const handleToggleStatus = async (targetUserId, currentStatus) => {
    try {
      await toggleUserStatus(targetUserId, !currentStatus, authToken);
      showToast(`User ${targetUserId} status updated`);
      await loadBackendData();
    } catch (err) {
      showToast(err?.message || 'Failed to update user status', 'error');
    }
  };

  return (
    <div>
      {/* Real Backend Metrics */}
      <div className="dash-metrics-grid">
        <div className="dash-metric-card">
          <div className="dash-metric-title">Tenant Institution</div>
          <div className="dash-metric-val">{currentUser?.tenant_id || 'SRIT-ATP'}</div>
          <div className="dash-metric-sub" style={{ color: '#10b981' }}>Live Database Schema Isolation</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Registered Accounts (Backend)</div>
          <div className="dash-metric-val" style={{ color: '#38bdf8' }}>
            {loadingUsers ? 'Loading...' : `${users.length} Users`}
          </div>
          <div className="dash-metric-sub" style={{ color: '#94a3b8' }}>Fetched directly from identity_service</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Dynamic Roles in DB</div>
          <div className="dash-metric-val" style={{ color: '#8b5cf6' }}>
            {loadingRoles ? 'Loading...' : `${roles.length} Roles`}
          </div>
          <div className="dash-metric-sub" style={{ color: '#34d399' }}>Configured in Supabase database</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Admin Account</div>
          <div className="dash-metric-val" style={{ color: '#ef4444', fontSize: '1.25rem' }}>
            {currentUser?.user_id}
          </div>
          <div className="dash-metric-sub" style={{ color: '#10b981' }}>Active Session • Hierarchy Level 90+</div>
        </div>
      </div>

      {/* Staff Provisioning Form (Sends Real Request to POST /api/v1/auth/provision-user) */}
      <div className="dash-feature-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '8px', borderRadius: '8px' }}>
            <UserCheck size={20} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Provision Faculty, HOD or Staff Account</h3>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>Submits real insert to Supabase database via identity service</p>
          </div>
        </div>

        <form onSubmit={handleProvisionSubmit} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px', alignItems: 'end' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', color: '#94a3b8', marginBottom: '6px' }}>Staff ID / Code</label>
            <input
              type="text"
              required
              value={staffForm.staff_id}
              onChange={(e) => setStaffForm({ ...staffForm, staff_id: e.target.value })}
              placeholder="e.g. FAC-SRIT-002"
              style={{ width: '100%', padding: '10px', background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#fff', boxSizing: 'border-box' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', color: '#94a3b8', marginBottom: '6px' }}>Full Name</label>
            <input
              type="text"
              required
              value={staffForm.full_name}
              onChange={(e) => setStaffForm({ ...staffForm, full_name: e.target.value })}
              placeholder="e.g. Dr. Ramesh Babu"
              style={{ width: '100%', padding: '10px', background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#fff', boxSizing: 'border-box' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', color: '#94a3b8', marginBottom: '6px' }}>Email Address</label>
            <input
              type="email"
              required
              value={staffForm.email}
              onChange={(e) => setStaffForm({ ...staffForm, email: e.target.value })}
              placeholder="staff@srit.ac.in"
              style={{ width: '100%', padding: '10px', background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#fff', boxSizing: 'border-box' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', color: '#94a3b8', marginBottom: '6px' }}>Initial Password</label>
            <input
              type="password"
              required
              value={staffForm.initial_password}
              onChange={(e) => setStaffForm({ ...staffForm, initial_password: e.target.value })}
              placeholder="••••••••"
              style={{ width: '100%', padding: '10px', background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#fff', boxSizing: 'border-box' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', color: '#94a3b8', marginBottom: '6px' }}>Assigned Role</label>
            <select
              value={staffForm.role_id}
              onChange={(e) => setStaffForm({ ...staffForm, role_id: e.target.value })}
              style={{ width: '100%', padding: '10px', background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#fff', boxSizing: 'border-box' }}
            >
              {roles.length > 0 ? (
                roles.filter(r => r.role_id !== 'ROLE_STUDENT').map(r => (
                  <option key={r.role_id} value={r.role_id}>{r.name} ({r.role_id})</option>
                ))
              ) : (
                <option value="">Fetching system roles from backend...</option>
              )}
            </select>
          </div>

          <div>
            <button
              type="submit"
              disabled={provisioning}
              style={{
                width: '100%',
                background: 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)',
                color: '#fff',
                padding: '11px',
                borderRadius: '8px',
                border: 'none',
                fontWeight: '700',
                cursor: 'pointer'
              }}
            >
              {provisioning ? 'Provisioning...' : 'Provision Staff'}
            </button>
          </div>
        </form>

        {provisionError && (
          <div style={{ marginTop: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '10px', borderRadius: '8px', color: '#f87171', fontSize: '0.82rem' }}>
            {provisionError}
          </div>
        )}
      </div>

      {/* Backend Assigned User Options */}
      <div className="dash-feature-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '8px', borderRadius: '8px' }}>
            <ShieldCheck size={20} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Institutional Administrator Privileges</h3>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>
              Role: <b>{currentRoleDetails?.name || currentUser?.role_name || 'Administrator'}</b> • Hierarchy Level {currentRoleDetails?.hierarchy_level || 90}
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px' }}>
          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Settings size={18} color="#ef4444" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Tenant Multi-Tenancy Control</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Configure institutional quota limits and tenant domain policies for {currentUser?.tenant_id}.</p>
          </div>

          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Layers size={18} color="#8b5cf6" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>Role Hierarchy Governance</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Manage system permission sets and dynamic RBAC roles across campus divisions.</p>
          </div>

          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <FileSpreadsheet size={18} color="#10b981" />
              <h4 style={{ margin: 0, fontSize: '0.92rem', color: '#fff' }}>NAAC & Accreditation Exports</h4>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Export audit-ready evidence for NBA, NAAC, and JNTUA regulatory reviews.</p>
          </div>
        </div>

        {userPermissions.length > 0 && (
          <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid #334155' }}>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: '600' }}>Backend Granted Permissions: </span>
            <div style={{ display: 'inline-flex', gap: '6px', flexWrap: 'wrap', marginLeft: '6px' }}>
              {userPermissions.map((perm) => (
                <span key={perm} style={{ fontSize: '0.72rem', background: '#090d16', color: '#ef4444', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(239, 68, 68, 0.3)', fontFamily: 'monospace' }}>
                  {perm}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Dynamic Roles List from Backend Database */}
      <div className="dash-feature-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Dynamic Roles Directory</h3>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>Live roles configuration from GET /api/v1/roles</p>
          </div>
          <span style={{ fontSize: '0.75rem', color: '#8b5cf6', background: 'rgba(139, 92, 246, 0.1)', padding: '4px 10px', borderRadius: '6px', border: '1px solid rgba(139, 92, 246, 0.3)' }}>
            {roles.length} Dynamic Roles Registered
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '10px' }}>
          {roles.map((r) => (
            <div key={r.role_id} style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <b style={{ color: '#fff', fontSize: '0.88rem' }}>{r.name}</b>
                <span style={{ fontSize: '0.7rem', color: '#38bdf8', fontFamily: 'monospace' }}>Lvl {r.hierarchy_level}</span>
              </div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '6px' }}>{r.description || 'System Role'}</div>
              <span style={{ fontSize: '0.7rem', color: '#10b981', background: '#090d16', padding: '2px 6px', borderRadius: '4px', fontFamily: 'monospace' }}>
                {r.role_id}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Real Registered Users List Fetched from Database */}
      <div className="dash-feature-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Tenant Users Roster</h3>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>Live accounts from GET /api/v1/users</p>
          </div>
          <button
            onClick={loadBackendData}
            style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#1e293b', border: '1px solid #334155', color: '#cbd5e1', padding: '6px 12px', borderRadius: '6px', fontSize: '0.8rem', cursor: 'pointer' }}
          >
            <RefreshCw size={14} /> Refresh Roster
          </button>
        </div>

        {loadingUsers ? (
          <div style={{ color: '#94a3b8', fontSize: '0.88rem', padding: '20px 0' }}>Querying Supabase database...</div>
        ) : users.length === 0 ? (
          <div style={{ color: '#64748b', fontSize: '0.88rem' }}>No users found in current tenant.</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {users.map((u) => (
              <div key={u.user_id} className="dash-table-row">
                <div>
                  <b style={{ color: '#fff', fontSize: '0.92rem' }}>{u.full_name}</b>
                  <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                    ID: <span style={{ color: '#38bdf8' }}>{u.user_id}</span> • {u.email} • Dept: {u.department}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{ fontSize: '0.75rem', background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8', padding: '3px 8px', borderRadius: '4px', fontWeight: '600' }}>
                    {u.role_name || u.role_id}
                  </span>
                  <button
                    onClick={() => handleToggleStatus(u.user_id, u.is_active)}
                    style={{
                      background: u.is_active ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                      border: `1px solid ${u.is_active ? '#10b981' : '#ef4444'}`,
                      color: u.is_active ? '#34d399' : '#f87171',
                      padding: '4px 10px',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: '700',
                      cursor: 'pointer'
                    }}
                  >
                    {u.is_active ? 'Active' : 'Disabled'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
