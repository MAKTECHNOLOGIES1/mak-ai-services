import React from 'react';
import { RouterProvider, useRouter } from './router/Router';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ROUTES } from './config/routes';

// Layouts
import MainLayout from './layouts/MainLayout';
import DashboardLayout from './layouts/DashboardLayout';

// Public Pages
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

// Role Dashboards
import StudentDashboard from './pages/dashboards/StudentDashboard';
import FacultyDashboard from './pages/dashboards/FacultyDashboard';
import HodDashboard from './pages/dashboards/HodDashboard';
import TpoDashboard from './pages/dashboards/TpoDashboard';
import AdminDashboard from './pages/dashboards/AdminDashboard';
import TrainerDashboard from './pages/dashboards/TrainerDashboard';
import LeadDashboard from './pages/dashboards/LeadDashboard';

// Common Components
import Toast from './components/Toast';
import AuthModal from './components/AuthModal';

function AppContent() {
  const { currentPath } = useRouter();
  const { toast, authModal, closeAuthModal } = useAuth();

  // Route Switcher based on current URL path
  const renderRoute = () => {
    switch (currentPath) {
      case ROUTES.HOME:
        return (
          <MainLayout>
            <HomePage />
          </MainLayout>
        );

      case ROUTES.LOGIN:
        return (
          <MainLayout>
            <LoginPage />
          </MainLayout>
        );

      case ROUTES.REGISTER:
        return (
          <MainLayout>
            <RegisterPage />
          </MainLayout>
        );

      // Dedicated Role Dashboards (100vh fit screen with scrollable content)
      case ROUTES.STUDENT_DASHBOARD:
        return (
          <DashboardLayout>
            <StudentDashboard />
          </DashboardLayout>
        );

      case ROUTES.FACULTY_DASHBOARD:
        return (
          <DashboardLayout>
            <FacultyDashboard />
          </DashboardLayout>
        );

      case ROUTES.HOD_DASHBOARD:
        return (
          <DashboardLayout>
            <HodDashboard />
          </DashboardLayout>
        );

      case ROUTES.TPO_DASHBOARD:
        return (
          <DashboardLayout>
            <TpoDashboard />
          </DashboardLayout>
        );

      case ROUTES.ADMIN_DASHBOARD:
        return (
          <DashboardLayout>
            <AdminDashboard />
          </DashboardLayout>
        );

      case ROUTES.TRAINER_DASHBOARD:
        return (
          <DashboardLayout>
            <TrainerDashboard />
          </DashboardLayout>
        );

      case ROUTES.LEAD_DASHBOARD:
        return (
          <DashboardLayout>
            <LeadDashboard />
          </DashboardLayout>
        );

      default:
        // Default fallback to HomePage for unknown paths
        return (
          <MainLayout>
            <HomePage />
          </MainLayout>
        );
    }
  };

  return (
    <>
      <Toast toast={toast} />
      <AuthModal
        isOpen={authModal?.isOpen}
        initialTab={authModal?.tab || 'login'}
        onClose={closeAuthModal}
      />
      {renderRoute()}
    </>
  );
}

export default function App() {
  return (
    <RouterProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </RouterProvider>
  );
}
