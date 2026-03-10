import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuthStore } from './services/auth';
import LoginPage from './components/auth/LoginPage';
import AppShell from './components/layout/AppShell';
import GroupsPage from './components/groups/GroupsPage';

function RequireAuth({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token);
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <AppShell />
          </RequireAuth>
        }
      >
        <Route index element={<Navigate to="/groups" replace />} />
        <Route path="groups" element={<GroupsPage />} />
        <Route path="groups/:groupId/studies" element={<div>Studies</div>} />
        <Route path="studies/:studyId" element={<div>Study</div>} />
      </Route>
    </Routes>
  );
}

export default App;
