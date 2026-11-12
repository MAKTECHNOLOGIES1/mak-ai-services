// Centralized API Configuration for AMK Platform
// Connects UI directly to Cloudflare Workers API Gateway & Microservices
// STRICT RULE: No localhost URLs allowed in this repository

export const API_CONFIG = {
  GATEWAY_URL: 'https://mak-api-gateway-test.anilkumarreddy3029.workers.dev',
  IDENTITY_URL: 'https://mak-identity-service-test.anilkumarreddy3029.workers.dev',
  DEFAULT_TENANT: 'SRIT-ATP',
  ENDPOINTS: {
    AUTH_LOGIN: '/api/v1/auth/login',
    AUTH_REGISTER_STUDENT: '/api/v1/auth/register/student',
    AUTH_PROVISION_USER: '/api/v1/auth/provision-user',
    AUTH_ME: '/api/v1/auth/me',
    ROLES: '/api/v1/roles',
    USERS: '/api/v1/users',
    HEALTH: '/health'
  }
};

export const getApiBaseUrl = () => {
  return localStorage.getItem('mak_api_gateway_url') || API_CONFIG.GATEWAY_URL;
};

export const setApiBaseUrl = (url) => {
  localStorage.setItem('mak_api_gateway_url', url);
};

