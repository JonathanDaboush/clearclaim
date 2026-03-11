import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/stores/authStore';
import { AppLayout } from '@/components/layout/AppLayout';
import { RequireAuth } from '@/components/layout/RequireAuth';

// Pages
import LoginPage              from '@/pages/LoginPage';
import SignupPage             from '@/pages/SignupPage';
import DashboardPage          from '@/pages/DashboardPage';
import ProjectsPage           from '@/pages/ProjectsPage';
import ProjectWorkspacePage   from '@/pages/ProjectWorkspacePage';
import ContractDetailPage     from '@/pages/ContractDetailPage';
import DevicesPage            from '@/pages/DevicesPage';
import PrivacyPage            from '@/pages/PrivacyPage';
import NotificationsPage      from '@/pages/NotificationsPage';
import AccountPage                from '@/pages/AccountPage';
import BillingPage                from '@/pages/BillingPage';
import ForgotPasswordPage         from '@/pages/ForgotPasswordPage';
import EvidencePage               from '@/pages/EvidencePage';
import NewDeviceVerificationPage  from '@/pages/NewDeviceVerificationPage';
import SecurityAlertsPage         from '@/pages/SecurityAlertsPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/login"           element={<LoginPage />} />
            <Route path="/signup"          element={<SignupPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/new-device"      element={<NewDeviceVerificationPage />} />

            {/* Protected routes */}
            <Route element={<RequireAuth />}>
              <Route element={<AppLayout />}>
                <Route path="/dashboard"                                       element={<DashboardPage />} />
                <Route path="/projects"                                        element={<ProjectsPage />} />
                <Route path="/projects/:projectId"                             element={<ProjectWorkspacePage />} />
                <Route path="/projects/:projectId/contracts/:contractId"       element={<ContractDetailPage />} />
                <Route path="/contracts/:contractId"                           element={<ContractDetailPage />} />
                <Route path="/notifications"                                   element={<NotificationsPage />} />
                <Route path="/devices"                                         element={<DevicesPage />} />
                <Route path="/account"                                         element={<AccountPage />} />
                <Route path="/billing"                                         element={<BillingPage />} />
                <Route path="/privacy"          element={<PrivacyPage />} />
                <Route path="/evidence"         element={<EvidencePage />} />
                <Route path="/security-alerts"  element={<SecurityAlertsPage />} />
              </Route>
            </Route>

            {/* Default redirect */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
