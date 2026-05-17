import { useEffect, useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { AuthPage } from "./pages/parent/AuthPage";
import { Dashboard } from "./pages/parent/Dashboard";
import { ProgressDashboard } from "./pages/parent/ProgressDashboard";
import { DiagnosticIntro } from "./pages/child/DiagnosticIntro";
import { DiagnosticExam } from "./pages/child/DiagnosticExam";
import { DiagnosticResult } from "./pages/child/DiagnosticResult";
import { ChildPath } from "./pages/child/ChildPath";
import { LessonPage } from "./pages/child/LessonPage";
import { SessionIntro } from "./pages/child/SessionIntro";
import { SessionComplete } from "./pages/child/SessionComplete";
import { DailyLimit } from "./pages/child/DailyLimit";
import { useAuthStore } from "./store/useAuthStore";
import "./App.css";

const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return isAuthenticated ? children : <Navigate to="/" />;
};

function App() {
  const { hydrate } = useAuthStore();
  const [isHydrating, setIsHydrating] = useState(true);

  useEffect(() => {
    const initApp = async () => {
      await hydrate();
      setIsHydrating(false);
    };
    initApp();
  }, [hydrate]);

  if (isHydrating) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          backgroundColor: "var(--color-bg)",
        }}
      >
        <h2 style={{ color: "var(--color-primary)" }}>Cargando Appfasia...</h2>
      </div>
    );
  }

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
          path="/parent/progress/:childId"
          element={
            <ProtectedRoute>
              <ProgressDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/child/diagnostic/intro"
          element={
            <ProtectedRoute>
              <DiagnosticIntro />
            </ProtectedRoute>
          }
        />
        <Route
          path="/child/diagnostic/exam"
          element={
            <ProtectedRoute>
              <DiagnosticExam />
            </ProtectedRoute>
          }
        />
        <Route
          path="/child/diagnostic/result"
          element={
            <ProtectedRoute>
              <DiagnosticResult />
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
        <Route
          path="/child/lesson/intro"
          element={
            <ProtectedRoute>
              <SessionIntro />
            </ProtectedRoute>
          }
        />
        <Route
          path="/child/lesson"
          element={
            <ProtectedRoute>
              <LessonPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/child/lesson/complete"
          element={
            <ProtectedRoute>
              <SessionComplete />
            </ProtectedRoute>
          }
        />
        <Route
          path="/child/lesson/limit"
          element={
            <ProtectedRoute>
              <DailyLimit />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
