import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuthStore } from "../../store/useAuthStore";
import { apiClient } from "../../services/apiClient";
import { ChatbotFab } from "../../components/Chatbot/ChatbotFab";
import "./Dashboard.css";

export const ProgressDashboard = () => {
  const { childId } = useParams();
  const navigate = useNavigate();
  const [childInfo, setChildInfo] = useState<any>(null);
  const [sessions, setSessions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        const [childRes, sessionsRes] = await Promise.all([
          apiClient.get(`/progress/${childId}`),
          apiClient.get(`/progress/${childId}/sessions`),
        ]);
        setChildInfo(childRes.data);
        setSessions(sessionsRes.data.sesiones || []);
      } catch (e) {
        console.error("Error fetching progress", e);
      } finally {
        setIsLoading(false);
      }
    };
    fetchProgress();
  }, [childId]);

  const handleShare = () => {
    alert("Generando enlace para compartir con el terapeuta...");
  };

  if (isLoading) return <div>Cargando progreso...</div>;

  return (
    <div className="dashboard-container" style={{ padding: "2rem" }}>
      <header className="top-bar">
        <button className="back-btn" onClick={() => navigate("/dashboard")}>
          Volver
        </button>
        <h2 style={{ color: "var(--color-primary)" }}>
          Progreso de {childInfo?.resumen_semana?.nombre || "Cargando..."}
        </h2>
        <button className="btn-primary" onClick={handleShare}>
          Compartir Reporte
        </button>
      </header>

      <section style={{ marginTop: "2rem" }}>
        <h3>Resumen Semanal</h3>
        <div className="feed-grid" style={{ marginTop: "1rem" }}>
          <div className="pub-card" style={{ textAlign: "center" }}>
            <h2>{childInfo?.resumen_semana?.hitos_dominados || 0}</h2>
            <p>Hitos dominados</p>
          </div>
          <div className="pub-card" style={{ textAlign: "center" }}>
            <h2>{childInfo?.resumen_semana?.sesiones_jugadas || 0}</h2>
            <p>Sesiones esta semana</p>
          </div>
        </div>
      </section>

      <section style={{ marginTop: "2rem" }}>
        <h3>Historial de Sesiones (P-04 & P-05)</h3>
        {sessions.length === 0 ? (
          <p>No hay sesiones registradas.</p>
        ) : (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "1rem",
              marginTop: "1rem",
            }}
          >
            {sessions.map((session, i) => (
              <div
                key={session.id_sesion || i}
                className="pub-card"
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <strong>
                    {new Date(session.fecha_inicio).toLocaleDateString()}
                  </strong>{" "}
                  - {session.estado}
                  <p
                    style={{
                      margin: "0.5rem 0 0",
                      color: "var(--color-text-muted)",
                    }}
                  >
                    Ejercicios: {session.ejercicios_completados} | Precisión:{" "}
                    {session.ipf_promedio}%
                  </p>
                </div>
                <button
                  className="btn-secondary"
                  onClick={() =>
                    alert("Mostrando detalle de ejercicios de la sesión...")
                  }
                >
                  Ver detalle
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      <ChatbotFab />
    </div>
  );
};
