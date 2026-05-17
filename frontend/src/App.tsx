import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { AuthPage } from "./pages/parent/AuthPage";
import { Dashboard } from "./pages/parent/Dashboard";
import { DiagnosticExam } from "./pages/child/DiagnosticExam";
import { ChildPath } from "./pages/child/ChildPath";
import { useAuthStore } from "./store/useAuthStore";
import "./App.css";

const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return isAuthenticated ? children : <Navigate to="/" />;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AuthPage />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/child/diagnostic"
          element={
            <ProtectedRoute>
              <DiagnosticExam />
            </ProtectedRoute>
          }
        />
        <Route
          path="/child/path"
          element={
            <ProtectedRoute>
              <ChildPath />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
