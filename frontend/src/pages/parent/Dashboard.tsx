import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../../store/useAuthStore";
import { Logo } from "../../components/Logo";
import { ChatbotFab } from "../../components/Chatbot/ChatbotFab";
import "./Dashboard.css";

export const Dashboard = () => {
  const { tutorName, logout } = useAuthStore();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("tutor");

  const carouselRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const startDragging = (e: React.MouseEvent) => {
    if (!carouselRef.current) return;
    setIsDragging(true);
    setStartX(e.pageX - carouselRef.current.offsetLeft);
    setScrollLeft(carouselRef.current.scrollLeft);
  };

  const stopDragging = () => {
    setIsDragging(false);
  };

  const onDrag = (e: React.MouseEvent) => {
    if (!isDragging || !carouselRef.current) return;
    e.preventDefault();
    const x = e.pageX - carouselRef.current.offsetLeft;
    const walk = (x - startX) * 1.3;
    carouselRef.current.scrollLeft = scrollLeft - walk;
  };

  const ninos = [];

  const publicaciones = [];

  return (
    <div className="dashboard-container">
      {/* 1. Top Bar */}
      <header className="top-bar">
        <div className="top-bar-logo">
          <div
            style={{
              transform: "scale(1.4)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Logo size={28} />
          </div>
          <h2
            style={{
              color: "var(--color-primary)",
              fontSize: "1.5rem",
              margin: "0 0 0 8px",
              fontWeight: 800,
              letterSpacing: "-0.02em",
            }}
          >
            Appfasia
          </h2>
        </div>
        <button className="logout-btn" onClick={handleLogout}>
          <span>Cerrar sesión</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
        </button>
      </header>

      {/* 2. Sección de niños */}
      <section className="children-section">
        {ninos.length > 0 ? (
          <div
            className="children-carousel"
            ref={carouselRef}
            onMouseDown={startDragging}
            onMouseLeave={stopDragging}
            onMouseUp={stopDragging}
            onMouseMove={onDrag}
          >
            {ninos.map((nino) => (
              <div key={nino.id} className="child-card">
                <div className="child-avatar-container">
                  <img
                    src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${nino.seed}&backgroundColor=f1f5f9`}
                    alt={nino.nombre}
                    className="child-avatar"
                  />
                  <div className="child-name">{nino.nombre}</div>
                </div>
                <div className="child-stats">
                  <h4>Métricas:</h4>
                  <ul>
                    <li>🔥 Racha: {nino.racha} días</li>
                    <li>⭐ Nivel: {nino.nivel}</li>
                    <li>📈 Progreso: {nino.progreso}</li>
                  </ul>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state-card">
            <div className="empty-state-icon">👶</div>
            <p className="empty-state-text">
              ¡Aún no has registrado a ningún niño!
              <br />
              Comienza añadiendo un perfil para ver su progreso.
            </p>
          </div>
        )}
        <button className="add-child-btn-large">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Agregar nuevo niño
        </button>
      </section>

      {/* 3. Feed de publicaciones */}
      <section className="feed-section">
        <h3
          style={{
            marginBottom: "1.5rem",
            color: "var(--color-text-main)",
            fontFamily: "var(--font-kids)",
            fontWeight: 800,
            fontSize: "1.4rem",
          }}
        >
          Últimas Novedades
        </h3>
        {publicaciones.length > 0 ? (
          <div className="feed-grid">
            {publicaciones.map((pub) => (
              <div key={pub.id} className="pub-card">
                <div className="pub-title">{pub.titulo}</div>
                <div className="pub-content">{pub.resumen}</div>
                <div className="pub-footer">
                  <span>{pub.tags}</span>
                  <span style={{ opacity: 0.7 }}>⏱ {pub.tiempo}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state-feed">
            <p>
              No hay novedades publicadas en este momento. ¡Vuelve más tarde!
            </p>
          </div>
        )}
      </section>

      {/* 4. Chatbot Flotante */}
      <ChatbotFab />

      {/* 5. Bottom Bar */}
      <nav className="bottom-bar">
        <button
          className={`bottom-bar-btn ${activeTab === "tutor" ? "active" : ""}`}
          onClick={() => setActiveTab("tutor")}
        >
          Modo tutor
        </button>
        <button
          className={`bottom-bar-btn ${activeTab === "nino" ? "active" : ""}`}
          onClick={() => {
            setActiveTab("nino");
            navigate("/child/diagnostic");
          }}
        >
          Modo niño
        </button>
      </nav>
    </div>
  );
};
