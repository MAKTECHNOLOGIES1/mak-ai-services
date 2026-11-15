// Centralized Tenant Service Client for AMK Platform
// Connects to Cloudflare Workers API Gateway (/api/v1/tenants/*)

import { API_CONFIG, getApiBaseUrl } from '../config/api';

function getAuthHeaders(token) {
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export async function fetchCurrentTenant(token) {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}${API_CONFIG.ENDPOINTS.TENANT_CURRENT}`, {
    method: 'GET',
    headers: getAuthHeaders(token)
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to fetch current college profile.');
  }
  return data;
}

export async function fetchTenantStats(tenantId, token) {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}${API_CONFIG.ENDPOINTS.TENANTS}/${encodeURIComponent(tenantId)}/stats`, {
    method: 'GET',
    headers: getAuthHeaders(token)
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to load seat capacity statistics.');
  }
  return data;
}

export async function fetchTenantModules(tenantId, token) {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}${API_CONFIG.ENDPOINTS.TENANTS}/${encodeURIComponent(tenantId)}/modules`, {
    method: 'GET',
    headers: getAuthHeaders(token)
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to fetch enabled modules.');
  }
  return data;
}

export async function toggleTenantModule(tenantId, moduleKey, isEnabled, token) {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}${API_CONFIG.ENDPOINTS.TENANTS}/${encodeURIComponent(tenantId)}/modules/toggle`, {
    method: 'POST',
    headers: getAuthHeaders(token),
    body: JSON.stringify({ module_key: moduleKey, is_enabled: isEnabled })
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || `Failed to toggle module ${moduleKey}.`);
  }
  return data;
}

export async function updateTenantDetails(tenantId, payload, token) {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}${API_CONFIG.ENDPOINTS.TENANTS}/${encodeURIComponent(tenantId)}`, {
    method: 'PATCH',
    headers: getAuthHeaders(token),
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to update college settings.');
  }
  return data;
}

export async function listAllTenants(token) {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}${API_CONFIG.ENDPOINTS.TENANTS}`, {
    method: 'GET',
    headers: getAuthHeaders(token)
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to list college tenants.');
  }
  return data;
}

