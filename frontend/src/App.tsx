import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuthStore } from './services/auth';
import LoginPage from './components/auth/LoginPage';
import AppShell from './components/layout/AppShell';
import GroupsPage from './components/groups/GroupsPage';
import StudiesPage from './pages/StudiesPage';
import StudyPage from './pages/StudyPage';
import ResultsPage from './pages/ResultsPage';
import AdminPage from './pages/AdminPage';

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
        <Route path="groups/:groupId/studies" element={<StudiesPage />} />
        <Route path="studies/:studyId" element={<StudyPage />} />
        <Route path="studies/:studyId/results" element={<ResultsPage />} />
        <Route path="admin" element={<AdminPage />} />
      </Route>
    </Routes>
  );
}

export default App;
