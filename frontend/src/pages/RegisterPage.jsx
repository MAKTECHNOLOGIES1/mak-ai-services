import React, { useState } from 'react';
import { UserPlus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Link } from '../router/Router';
import { ROUTES } from '../config/routes';
import './AuthPages.css';

export default function RegisterPage() {
  const { register } = useAuth();

  const [form, setForm] = useState({
    roll_number: '',
    email: '',
    full_name: '',
    password: '',
    department: 'CSE',
    batch_year: '',
    tenant_id: 'SRIT-ATP'
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await register(form);
    } catch (err) {
      setError(err?.message || 'Registration failed. Please verify the information and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '640px', margin: '40px auto 60px auto', padding: '0 20px' }}>
      <div style={{
        background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%)',
        border: '1px solid rgba(16, 185, 129, 0.25)',
        borderRadius: '20px',
        padding: '36px',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.6)'
      }}>
        
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '52px',
            height: '52px',
            borderRadius: '14px',
            background: 'rgba(16, 185, 129, 0.15)',
            color: '#10b981',
            marginBottom: '12px'
          }}>
            <UserPlus size={28} />
          </div>
          <h2 style={{ fontSize: '1.7rem', fontWeight: '800', margin: '0 0 6px 0', color: '#ffffff' }}>
            Student Registration
          </h2>
          <p style={{ margin: 0, fontSize: '0.88rem', color: '#94a3b8' }}>
            Create your account on the AMK Platform (SRIT-ATP • JNTUA Affiliated)
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', fontWeight: '600', marginBottom: '6px' }}>
              Student Roll Number
            </label>
            <input
              type="text"
              required
              value={form.roll_number}
              onChange={(e) => setForm({ ...form, roll_number: e.target.value })}
              placeholder="e.g. 22731A0501"
              style={{ width: '100%', padding: '11px', background: '#090d16', border: '1px solid #334155', borderRadius: '8px', color: '#fff', boxSizing: 'border-box' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', fontWeight: '600', marginBottom: '6px' }}>
              Full Name
            </label>
            <input
              type="text"
              required
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              placeholder="e.g. Rahul Sharma"
              style={{ width: '100%', padding: '11px', background: '#090d16', border: '1px solid #334155', borderRadius: '8px', color: '#fff', boxSizing: 'border-box' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', fontWeight: '600', marginBottom: '6px' }}>
              Email Address
            </label>
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="student@srit.ac.in"
              style={{ width: '100%', padding: '11px', background: '#090d16', border: '1px solid #334155', borderRadius: '8px', color: '#fff', boxSizing: 'border-box' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', fontWeight: '600', marginBottom: '6px' }}>
              Password
            </label>
            <input
              type="password"
              required
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="••••••••"
              style={{ width: '100%', padding: '11px', background: '#090d16', border: '1px solid #334155', borderRadius: '8px', color: '#fff', boxSizing: 'border-box' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', fontWeight: '600', marginBottom: '6px' }}>
              Department
            </label>
            <select
              value={form.department}
              onChange={(e) => setForm({ ...form, department: e.target.value })}
              style={{ width: '100%', padding: '11px', background: '#090d16', border: '1px solid #334155', borderRadius: '8px', color: '#fff', boxSizing: 'border-box' }}
            >
              <option value="CSE">Computer Science & Engineering</option>
              <option value="ECE">Electronics & Communication</option>
              <option value="AI_DS">AI & Data Science</option>
              <option value="MECH">Mechanical Engineering</option>
              <option value="CIVIL">Civil Engineering</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', fontWeight: '600', marginBottom: '6px' }}>
              Batch Year
            </label>
            <input
              type="text"
              value={form.batch_year}
              onChange={(e) => setForm({ ...form, batch_year: e.target.value })}
              style={{ width: '100%', padding: '11px', background: '#090d16', border: '1px solid #334155', borderRadius: '8px', color: '#fff', boxSizing: 'border-box' }}
            />
          </div>

          {error && (
            <div style={{ gridColumn: '1 / -1', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', padding: '10px 14px', color: '#f87171', fontSize: '0.82rem' }}>
              {error}
            </div>
          )}

          <div style={{ gridColumn: '1 / -1', marginTop: '10px' }}>
            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: '#ffffff',
                padding: '13px',
                borderRadius: '10px',
                border: 'none',
                fontSize: '0.95rem',
                fontWeight: '700',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                boxShadow: '0 4px 14px rgba(16, 185, 129, 0.4)'
              }}
            >
              <UserPlus size={18} />
              <span>{loading ? 'Creating Account...' : 'Complete Registration'}</span>
            </button>
          </div>
        </form>

        <div style={{ borderTop: '1px solid #1e293b', marginTop: '24px', paddingTop: '18px', textAlign: 'center', fontSize: '0.82rem', color: '#94a3b8' }}>
          Already have an account?{' '}
          <Link to={ROUTES.LOGIN} style={{ color: '#38bdf8', fontWeight: '600', textDecoration: 'none' }}>
            Sign In Here &rarr;
          </Link>
        </div>

      </div>
    </div>
  );
}

