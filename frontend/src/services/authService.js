// Unified Authentication Service for AMK Platform
// Connects to Cloudflare Workers API Gateway & Microservices (Zero Localhost)

import { API_CONFIG, getApiBaseUrl } from '../config/api';

export async function loginUser(identifier, password) {
  const base = getApiBaseUrl();
  const payload = {
    login_identifier: identifier.trim(),
    password: password
  };

  try {
    const res = await fetch(`${base}${API_CONFIG.ENDPOINTS.AUTH_LOGIN}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Login failed. Please verify credentials.');
    }
    return data;
  } catch (err) {
    // If gateway fails or network is offline, attempt direct connection to identity service
    if (base !== API_CONFIG.IDENTITY_URL && err.message?.includes('Failed to fetch')) {
      try {
        const directRes = await fetch(`${API_CONFIG.IDENTITY_URL}${API_CONFIG.ENDPOINTS.AUTH_LOGIN}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
          body: JSON.stringify(payload)
        });
        const directData = await directRes.json();
        if (directRes.ok) return directData;
      } catch {
        // Fall back to original error
      }
    }
    throw err;
  }
}

export async function registerStudent(studentData) {
  const base = getApiBaseUrl();
  const payload = {
    tenant_id: (studentData.tenant_id || API_CONFIG.DEFAULT_TENANT).trim(),
    roll_number: (studentData.roll_number || studentData.roll || '').trim().toUpperCase(),
    email: (studentData.email || '').trim().toLowerCase(),
    password: studentData.password,
    full_name: (studentData.full_name || '').trim(),
    department: (studentData.department || '').trim().toUpperCase(),
    batch_year: (studentData.batch_year || '').trim()
  };

  const res = await fetch(`${base}${API_CONFIG.ENDPOINTS.AUTH_REGISTER_STUDENT}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Student registration failed');
  }
  return data;
}

export async function provisionStaff(staffData, token) {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}${API_CONFIG.ENDPOINTS.AUTH_PROVISION_USER}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(staffData)
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Staff provisioning failed');
  }
  return data;
}

export async function fetchUserProfile(token) {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}${API_CONFIG.ENDPOINTS.AUTH_ME}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/json'
    }
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Session expired or invalid');
  }
  return data;
}

export async function fetchRoles() {
  const base = getApiBaseUrl();
  try {
    const res = await fetch(`${base}${API_CONFIG.ENDPOINTS.ROLES}`, {
      headers: { 'Accept': 'application/json' }
    });
    if (res.ok) return await res.json();
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'Failed to fetch roles from backend');
  } catch (e) {
    console.warn('Backend roles fetch error:', e?.message);
    throw e;
  }
}

export async function fetchTenantUsers(token, filters = {}) {
  const base = getApiBaseUrl();
  const params = new URLSearchParams();
  if (filters.role_id) params.append('role_id', filters.role_id);
  if (filters.department) params.append('department', filters.department);

  const query = params.toString() ? `?${params.toString()}` : '';
  const res = await fetch(`${base}${API_CONFIG.ENDPOINTS.USERS}${query}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/json'
    }
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to fetch users from database');
  }
  return data;
}

export async function toggleUserStatus(targetUserId, isActive, token) {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}${API_CONFIG.ENDPOINTS.USERS}/${targetUserId}/status?is_active=${isActive}`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/json'
    }
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to update user status');
  }
  return data;
}

export async function createRole(roleData, token) {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}${API_CONFIG.ENDPOINTS.ROLES}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/json'
    },
    body: JSON.stringify(roleData)
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to create dynamic role');
  }
  return data;
}

export async function fetchHealthCheck() {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}${API_CONFIG.ENDPOINTS.HEALTH}`);
  return await res.json();
}

