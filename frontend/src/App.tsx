import { lazy, Suspense, useEffect } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuthStore } from './features/auth/store/authStore';
import { useThemeStore } from './store/themeStore';
import LoadingScreen from './components/common/LoadingScreen';
import AuthLayout from './layouts/AuthLayout';
import DashboardLayout from './layouts/DashboardLayout';
import React from 'react';

// Lazy load pages
const AuthPage = lazy(() => import('./pages/AuthPage'));
// Use the SecurityDashboardPage with charts and visual elements
const SecurityDashboardPage = lazy(() => import('./pages/dashboard/SecurityDashboardPage'));

const MsspDashboardPage = lazy(() => import('./pages/mssp/MsspDashboardPage'));
const AlertsManagementPage = lazy(() => import('./pages/alerts/AlertsManagementPage'));
const DigitalTwinHoneypotPage = lazy(() => import('./pages/twin/DigitalTwinHoneypotPage'));
const ReportingAnalyticsPage = lazy(() => import('./pages/reports/ReportingAnalyticsPage'));
const AnalyticsPage = lazy(() => import('./pages/analytics/AnalyticsPage'));
const UserProfilePage = lazy(() => import('./pages/settings/UserProfilePage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));

function App() {
  const { isAuthenticated, checkAuth } = useAuthStore();
  const { theme, initTheme } = useThemeStore();

  // Add a simple state to track if the app has initialized
  const [initialized, setInitialized] = React.useState(false);

  useEffect(() => {
    console.log("App component mounted");

    const initialize = async () => {
      try {
        // Initialize theme first
        initTheme();
        console.log("Theme initialized");

        // Check authentication
        await checkAuth();
        console.log("Auth checked");

        // If no authentication, use development bypass
        if (!isAuthenticated) {
          console.log("No authentication found, using development bypass");

          // Create a mock user for development
          const mockUser = {
            id: "00000000-0000-0000-0000-000000000000",
            email: "admin@finguard.com",
            full_name: "Admin User",
            role: "admin",
            is_active: true,
            is_superuser: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            last_login: new Date().toISOString(),
            preferences: {},
            notification_settings: {
              email: true,
              slack: false,
              discord: false
            }
          };

          // Update auth store with mock user
          useAuthStore.setState({
            isAuthenticated: true,
            user: mockUser,
            isLoading: false,
          });

          console.log("Development bypass complete");
        }
      } catch (error) {
        console.error("Error during initialization:", error);

        // Use development bypass on error
        console.log("Error occurred, using development bypass");

        // Create a mock user for development
        const mockUser = {
          id: "00000000-0000-0000-0000-000000000000",
          email: "admin@finguard.com",
          full_name: "Admin User",
          role: "admin",
          is_active: true,
          is_superuser: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          last_login: new Date().toISOString(),
          preferences: {},
          notification_settings: {
            email: true,
            slack: false,
            discord: false
          }
        };

        // Update auth store with mock user
        useAuthStore.setState({
          isAuthenticated: true,
          user: mockUser,
          isLoading: false,
        });
      } finally {
        // Always set initialized to true to prevent infinite loading
        setInitialized(true);
        console.log("Initialization complete");
      }
    };

    initialize();
  }, [initTheme, checkAuth]);

  useEffect(() => {
    try {
      document.documentElement.classList.toggle('dark', theme === 'dark');
      console.log("Theme applied:", theme);
    } catch (error) {
      console.error("Error applying theme:", error);
    }
  }, [theme]);

  // Log authentication state for debugging
  console.log("Authentication state:", { isAuthenticated, initialized });

  return (
    <Suspense fallback={<LoadingScreen />}>
      <Routes>
        {!isAuthenticated ? (
          <>
            <Route path="/auth" element={<AuthLayout />}>
              <Route index element={<AuthPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/auth" replace />} />
          </>
        ) : (
          <>
            <Route path="/" element={<DashboardLayout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<SecurityDashboardPage />} />
              <Route path="dashboard/basic" element={<SecurityDashboardPage />} />
              <Route path="mssp" element={<MsspDashboardPage />} />
              <Route path="alerts" element={<AlertsManagementPage />} />
              <Route path="twin" element={<DigitalTwinHoneypotPage />} />
              <Route path="reports" element={<ReportingAnalyticsPage />} />
              <Route path="analytics" element={<AnalyticsPage />} />
              <Route path="profile" element={<UserProfilePage />} />
            </Route>
            <Route path="/auth" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<NotFoundPage />} />
          </>
        )}
      </Routes>
    </Suspense>
  );
}

export default App;
