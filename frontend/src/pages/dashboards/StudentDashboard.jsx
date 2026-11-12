import React, { useState } from 'react';
import {
  Search,
  Sparkles,
  BookOpen,
  FolderGit2,
  MessageSquare,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { API_CONFIG, getApiBaseUrl } from '../../config/api';
import './DashboardCommon.css';

export default function StudentDashboard() {
  const { currentUser, userPermissions, currentRoleDetails, showToast } = useAuth();

  const [ragQuery, setRagQuery] = useState('');
  const [ragResponse, setRagResponse] = useState('');
  const [ragError, setRagError] = useState('');
  const [searching, setSearching] = useState(false);

  // Live Query against Backend API Gateway (Zero mock fallbacks)
  const handleAskRag = async (e) => {
    e.preventDefault();
    if (!ragQuery.trim()) return;
    setSearching(true);
    setRagResponse('');
    setRagError('');

    try {
      const base = getApiBaseUrl();
      const res = await fetch(`${base}/api/v1/knowledge/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          query: ragQuery.trim(),
          department: currentUser?.department || '',
          tenant_id: currentUser?.tenant_id || ''
        })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Backend responded with HTTP ${res.status}`);
      }

      const data = await res.json();
      setRagResponse(data.answer || data.response || JSON.stringify(data));
      showToast('Knowledge query returned from backend');
    } catch (err) {
      setRagError(`Backend Knowledge Service: ${err.message}`);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div>
      {/* Real Student Identity & Metrics from Backend */}
      <div className="dash-metrics-grid">
        <div className="dash-metric-card">
          <div className="dash-metric-title">Universal User ID (Roll No)</div>
          <div className="dash-metric-val" style={{ color: '#38bdf8', fontSize: '1.5rem' }}>
            {currentUser?.user_id || 'Not Assigned'}
          </div>
          <div className="dash-metric-sub" style={{ color: '#10b981' }}>Universal Student Identifier in Supabase</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Department & Branch</div>
          <div className="dash-metric-val" style={{ fontSize: '1.4rem' }}>
            {currentUser?.department || 'Not Assigned'}
          </div>
          <div className="dash-metric-sub" style={{ color: '#94a3b8' }}>Enrolled Academic Division</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Academic Batch</div>
          <div className="dash-metric-val" style={{ color: '#8b5cf6', fontSize: '1.4rem' }}>
            {currentUser?.batch_year || 'Not Assigned'}
          </div>
          <div className="dash-metric-sub" style={{ color: '#34d399' }}>JNTUA Affiliated Graduation Cycle</div>
        </div>

        <div className="dash-metric-card">
          <div className="dash-metric-title">Institutional Tenant</div>
          <div className="dash-metric-val" style={{ color: '#10b981', fontSize: '1.4rem' }}>
            {currentUser?.tenant_id || 'Not Assigned'}
          </div>
          <div className="dash-metric-sub" style={{ color: currentUser?.is_active ? '#34d399' : '#f87171' }}>
            {currentUser?.is_active ? 'Active Enrolled Status' : 'Account Disabled'}
          </div>
        </div>
      </div>

      {/* Verified Account Details Card from Backend Response */}
      <div className="dash-feature-card">
        <h3 style={{ margin: '0 0 16px 0', fontSize: '1.1rem', color: '#fff' }}>Verified Student Academic Record</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
          <div style={{ background: '#1e293b', padding: '14px 18px', borderRadius: '10px' }}>
            <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Student Name</span>
            <div style={{ fontWeight: '700', color: '#fff', fontSize: '0.95rem' }}>{currentUser?.full_name || '-'}</div>
          </div>
          <div style={{ background: '#1e293b', padding: '14px 18px', borderRadius: '10px' }}>
            <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Email Address</span>
            <div style={{ fontWeight: '700', color: '#fff', fontSize: '0.95rem' }}>{currentUser?.email || '-'}</div>
          </div>
          <div style={{ background: '#1e293b', padding: '14px 18px', borderRadius: '10px' }}>
            <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Assigned System Role</span>
            <div style={{ fontWeight: '700', color: '#10b981', fontSize: '0.95rem' }}>{currentUser?.role_name || currentUser?.role_id || '-'}</div>
          </div>
        </div>
      </div>

      {/* Backend Assigned User Options & Permissions */}
      <div className="dash-feature-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <div style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', padding: '8px', borderRadius: '8px' }}>
            <ShieldCheck size={20} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Student Workspace Options (Granted by Backend)</h3>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>
              Role: <b>{currentRoleDetails?.name || currentUser?.role_name || currentUser?.role_id}</b> • Level {currentRoleDetails?.hierarchy_level || 10}
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '14px' }}>
          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
              <div style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', padding: '8px', borderRadius: '8px' }}>
                <BookOpen size={18} />
              </div>
              <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#fff' }}>Enrolled Curriculum</h4>
            </div>
            <p style={{ margin: '0 0 12px 0', fontSize: '0.8rem', color: '#94a3b8' }}>
              Department modules and autonomous syllabus for batch {currentUser?.batch_year || 'enrolled'}.
            </p>
            <span style={{ fontSize: '0.72rem', background: '#090d16', color: '#38bdf8', padding: '3px 8px', borderRadius: '4px', border: '1px solid #334155' }}>
              Scope: {currentUser?.department || 'Department'}
            </span>
          </div>

          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
              <div style={{ background: 'rgba(139, 92, 246, 0.15)', color: '#a78bfa', padding: '8px', borderRadius: '8px' }}>
                <FolderGit2 size={18} />
              </div>
              <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#fff' }}>Capstone Submissions</h4>
            </div>
            <p style={{ margin: '0 0 12px 0', fontSize: '0.8rem', color: '#94a3b8' }}>
              Multi-phase project submission tracking with Senior Tech Lead evaluations.
            </p>
            <span style={{ fontSize: '0.72rem', background: '#090d16', color: '#a78bfa', padding: '3px 8px', borderRadius: '4px', border: '1px solid #334155' }}>
              Status: Connected to Project Studio
            </span>
          </div>

          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
              <div style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', padding: '8px', borderRadius: '8px' }}>
                <MessageSquare size={18} />
              </div>
              <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#fff' }}>AI Academic Guidance</h4>
            </div>
            <p style={{ margin: '0 0 12px 0', fontSize: '0.8rem', color: '#94a3b8' }}>
              Semantic retrieval of academic regulations, attendance criteria, and exam formats.
            </p>
            <span style={{ fontSize: '0.72rem', background: '#090d16', color: '#34d399', padding: '3px 8px', borderRadius: '4px', border: '1px solid #334155' }}>
              Tenant: {currentUser?.tenant_id}
            </span>
          </div>
        </div>

        {userPermissions.length > 0 && (
          <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid #334155' }}>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: '600' }}>Backend Granted Permissions: </span>
            <div style={{ display: 'inline-flex', gap: '6px', flexWrap: 'wrap', marginLeft: '6px' }}>
              {userPermissions.map((perm) => (
                <span key={perm} style={{ fontSize: '0.72rem', background: '#090d16', color: '#10b981', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(16, 185, 129, 0.3)', fontFamily: 'monospace' }}>
                  {perm}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Live RAG Syllabus Query Box */}
      <div className="dash-feature-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
          <div style={{ background: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8', padding: '8px', borderRadius: '8px' }}>
            <Search size={20} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Syllabus & Academic Regulations Query</h3>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>Connects live to backend {API_CONFIG.GATEWAY_URL}/api/v1/knowledge/query</p>
          </div>
        </div>

        <form onSubmit={handleAskRag} className="dash-rag-container">
          <input
            type="text"
            value={ragQuery}
            onChange={(e) => setRagQuery(e.target.value)}
            placeholder="Ask question regarding attendance, detention, credits, or curriculum..."
            className="dash-rag-input"
          />
          <button
            type="submit"
            disabled={searching}
            className="btn-primary"
          >
            {searching ? 'Querying Backend...' : 'Ask AI'}
          </button>
        </form>

        {ragResponse && (
          <div className="dash-rag-result">
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#38bdf8', fontWeight: '700', marginBottom: '6px' }}>
              <Sparkles size={16} /> Backend Response:
            </div>
            {ragResponse}
          </div>
        )}

        {ragError && (
          <div style={{ marginTop: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '10px 14px', borderRadius: '8px', color: '#f87171', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={16} />
            <span>{ragError}</span>
          </div>
        )}
      </div>
    </div>
  );
}
