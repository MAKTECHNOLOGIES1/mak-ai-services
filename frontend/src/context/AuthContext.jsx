import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, registerStudent, fetchUserProfile, fetchRoles } from '../services/authService';
import { getDashboardRouteForRole, ROUTES } from '../config/routes';
import { useRouter } from '../router/Router';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const { navigate } = useRouter();

  const [authToken, setAuthToken] = useState(() => localStorage.getItem('mak_auth_token') || '');
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const saved = localStorage.getItem('mak_auth_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [systemRoles, setSystemRoles] = useState([]);
  const [toast, setToast] = useState(null);
  const [authModal, setAuthModal] = useState({ isOpen: false, tab: 'login' });

  const openAuthModal = (tab = 'login') => {
    setAuthModal({ isOpen: true, tab });
  };

  const closeAuthModal = () => {
    setAuthModal({ isOpen: false, tab: 'login' });
  };

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => {
      setToast(null);
    }, 4000);
  };

  const isLoggedIn = Boolean(authToken && currentUser);
  const currentRole = currentUser?.role_id || currentUser?.role || 'ROLE_STUDENT';

  // Load system dynamic roles from Backend
  useEffect(() => {
    fetchRoles()
      .then((roles) => {
        if (Array.isArray(roles)) {
          setSystemRoles(roles);
        }
      })
      .catch((err) => {
        console.warn('Backend dynamic roles fetch notice:', err?.message);
      });
  }, []);

  // Synchronize profile on initial token load from Backend
  useEffect(() => {
    if (authToken) {
      fetchUserProfile(authToken)
        .then((profile) => {
          setCurrentUser(profile);
          localStorage.setItem('mak_auth_user', JSON.stringify(profile));
        })
        .catch((err) => {
          console.warn('Session expired or invalid on backend, clearing state:', err?.message);
          setAuthToken('');
          setCurrentUser(null);
          localStorage.removeItem('mak_auth_token');
          localStorage.removeItem('mak_auth_user');
        });
    }
  }, [authToken]);

  // Derive role details and backend permissions for currently authenticated user
  const currentRoleDetails = systemRoles.find(r => r.role_id === currentRole) || null;
  const userPermissions = currentRoleDetails?.permissions || [];

  // Handle Real Login and auto-redirect strictly based on backend response
  const handleLogin = async (identifier, password) => {
    const res = await loginUser(identifier, password);
    
    // Store authenticated JWT token & user from backend
    setAuthToken(res.access_token);
    setCurrentUser(res.user);
    localStorage.setItem('mak_auth_token', res.access_token);
    localStorage.setItem('mak_auth_user', JSON.stringify(res.user));
    
    // Read the role_id returned from backend
    const role = res.user.role_id || res.user.role || 'ROLE_STUDENT';
    const targetDashboard = getDashboardRouteForRole(role);
    
    showToast(`Welcome back, ${res.user.full_name}! Redirecting to ${role.replace('ROLE_', '')} Dashboard.`);
    navigate(targetDashboard);
    return res;
  };

  // Switch role view strictly for authorized role navigation
  const handleSwitchRole = (newRoleId) => {
    const targetDashboard = getDashboardRouteForRole(newRoleId);
    showToast(`Switched view to ${newRoleId.replace('ROLE_', '')}`);
    navigate(targetDashboard);
  };

  // Registration
  const handleRegister = async (studentData) => {
    const res = await registerStudent(studentData);
    if (res.access_token && res.user) {
      setAuthToken(res.access_token);
      setCurrentUser(res.user);
      localStorage.setItem('mak_auth_token', res.access_token);
      localStorage.setItem('mak_auth_user', JSON.stringify(res.user));
      navigate(ROUTES.STUDENT_DASHBOARD);
    }
    return res;
  };

  // Logout
  const handleLogout = () => {
    setAuthToken('');
    setCurrentUser(null);
    localStorage.removeItem('mak_auth_token');
    localStorage.removeItem('mak_auth_user');
    showToast('Securely signed out.', 'info');
    navigate(ROUTES.LOGIN);
  };

  return (
    <AuthContext.Provider value={{
      authToken,
      currentUser,
      isLoggedIn,
      currentRole,
      systemRoles,
      currentRoleDetails,
      userPermissions,
      toast,
      showToast,
      authModal,
      openAuthModal,
      closeAuthModal,
      login: handleLogin,
      switchRole: handleSwitchRole,
      register: handleRegister,
      logout: handleLogout
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

