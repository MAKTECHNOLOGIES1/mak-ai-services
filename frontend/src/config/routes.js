// Centralized Routes Configuration for AMK Platform
// All application URLs and role mappings are defined here for easy maintenance

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  
  // Role-specific Dashboards
  STUDENT_DASHBOARD: '/student-dashboard',
  FACULTY_DASHBOARD: '/faculty-dashboard',
  HOD_DASHBOARD: '/hod-dashboard',
  TPO_DASHBOARD: '/tpo-dashboard',
  ADMIN_DASHBOARD: '/admin-dashboard',
  TRAINER_DASHBOARD: '/trainer-dashboard',
  LEAD_DASHBOARD: '/lead-dashboard'
};

// Map each role to its dedicated dashboard URL
export const ROLE_DASHBOARDS = {
  ROLE_STUDENT: ROUTES.STUDENT_DASHBOARD,
  ROLE_FACULTY: ROUTES.FACULTY_DASHBOARD,
  ROLE_HOD: ROUTES.HOD_DASHBOARD,
  ROLE_TPO: ROUTES.TPO_DASHBOARD,
  ROLE_ADMIN: ROUTES.ADMIN_DASHBOARD,
  ROLE_SUPER_ADMIN: ROUTES.ADMIN_DASHBOARD,
  ROLE_TRAINER: ROUTES.TRAINER_DASHBOARD,
  ROLE_SR_LEAD: ROUTES.LEAD_DASHBOARD,
  ROLE_TECHNICAL_MANAGER: ROUTES.LEAD_DASHBOARD
};

// Helper: Resolve dashboard URL based on role
export const getDashboardRouteForRole = (role) => {
  return ROLE_DASHBOARDS[role] || ROUTES.STUDENT_DASHBOARD;
};

// Available Roles Metadata
export const ROLES_METADATA = [
  { id: 'ROLE_STUDENT', name: 'Student', path: ROUTES.STUDENT_DASHBOARD, badge: 'Student', color: '#10b981', bg: 'rgba(16, 185, 129, 0.1)', border: '#059669', defaultId: '22731A0501' },
  { id: 'ROLE_FACULTY', name: 'Faculty', path: ROUTES.FACULTY_DASHBOARD, badge: 'Faculty Professor', color: '#6366f1', bg: 'rgba(99, 102, 241, 0.1)', border: '#4f46e5', defaultId: 'FAC-SRIT-001' },
  { id: 'ROLE_HOD', name: 'HOD', path: ROUTES.HOD_DASHBOARD, badge: 'Head of Department', color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.1)', border: '#7c3aed', defaultId: 'HOD-CSE-001' },
  { id: 'ROLE_TPO', name: 'TPO Officer', path: ROUTES.TPO_DASHBOARD, badge: 'Placement Officer', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)', border: '#d97706', defaultId: 'TPO-SRIT-001' },
  { id: 'ROLE_ADMIN', name: 'Principal / Admin', path: ROUTES.ADMIN_DASHBOARD, badge: 'Principal / Admin', color: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)', border: '#dc2626', defaultId: 'ADM-SRIT-001' },
  { id: 'ROLE_TRAINER', name: 'Tech Trainer', path: ROUTES.TRAINER_DASHBOARD, badge: 'Technical Trainer', color: '#06b6d4', bg: 'rgba(6, 182, 212, 0.1)', border: '#0891b2', defaultId: 'TRN-SRIT-001' },
  { id: 'ROLE_SR_LEAD', name: 'Senior Lead', path: ROUTES.LEAD_DASHBOARD, badge: 'Senior Tech Lead', color: '#ec4899', bg: 'rgba(236, 72, 153, 0.1)', border: '#db2777', defaultId: 'LEAD-SRIT-001' }
];

