import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../../store/useAuthStore";
import { useChildStore } from "../../store/useChildStore";
import {
  publicationsService,
  type Publication,
} from "../../services/publicationsService";
import { Logo } from "../../components/Logo";
import { ChatbotFab } from "../../components/Chatbot/ChatbotFab";
import { AddChildModal } from "../../components/AddChildModal";
import { ChildSelectorModal } from "../../components/ChildSelectorModal";
import "./Dashboard.css";

export const Dashboard = () => {
  const { tutorName, logout } = useAuthStore();
  const { children, fetchChildren, addChild, setActiveChild } = useChildStore();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("tutor");

  const [publicaciones, setPublicaciones] = useState<Publication[]>([]);
  const [isAddChildOpen, setIsAddChildOpen] = useState(false);
  const [isSelectorOpen, setIsSelectorOpen] = useState(false);

  const carouselRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);

  useEffect(() => {
    fetchChildren();

    const loadPubs = async () => {
      try {
        const pubs = await publicationsService.syncPublications();
        setPublicaciones(pubs);
      } catch (e) {
        console.error("Error al cargar publicaciones", e);
      }
    };
    loadPubs();
  }, [fetchChildren]);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const handleModoNino = () => {
    if (children.length === 0) {
      alert("Por favor agrega un niño primero.");
      return;
    }

    if (children.length === 1) {
      selectChild(children[0]);
    } else {
      setIsSelectorOpen(true);
    }
  };

  const selectChild = (child: any) => {
    setActiveChild(child);
    setIsSelectorOpen(false);
    setActiveTab("nino");
    if (child.diagnostico_ok) {
      navigate("/child/path");
    } else {
      navigate("/child/diagnostic/intro");
    }
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
        {children.length > 0 ? (
          <div
            className="children-carousel"
            ref={carouselRef}
            onMouseDown={startDragging}
            onMouseLeave={stopDragging}
            onMouseUp={stopDragging}
            onMouseMove={onDrag}
          >
            {children.map((nino) => (
              <div key={nino.id_child} className="child-card">
                <div className="child-avatar-container">
                  <img
                    src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${nino.id_child}&backgroundColor=f1f5f9`}
                    alt={nino.nombre}
                    className="child-avatar"
                  />
                  <div className="child-name">{nino.nombre}</div>
                </div>
                <div className="child-stats">
                  <h4>Métricas:</h4>
                  <ul>
                    <li>🔥 Racha: {nino.racha_dias} días</li>
                    <li>
                      ⭐ Nivel:{" "}
                      {nino.diagnostico_ok
                        ? nino.nivel_actual
                        : "No diagnosticado"}
                    </li>
                  </ul>
                  <button
                    className="btn-secondary"
                    style={{
                      width: "100%",
                      marginTop: "1rem",
                      padding: "0.5rem",
                    }}
                    onClick={() =>
                      navigate(`/parent/progress/${nino.id_child}`)
                    }
                  >
                    Ver progreso detallado
                  </button>
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
        <button
          className="add-child-btn-large"
          onClick={() => setIsAddChildOpen(true)}
        >
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
                  <span>{pub.tags.join(", ")}</span>
                  <span style={{ opacity: 0.7 }}>
                    ⏱ {pub.tiempo || "Reciente"}
                  </span>
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

      {/* Modales */}
      <AddChildModal
        isOpen={isAddChildOpen}
        onClose={() => setIsAddChildOpen(false)}
        onAdd={addChild}
      />
      <ChildSelectorModal
        isOpen={isSelectorOpen}
        onClose={() => setIsSelectorOpen(false)}
        childrenList={children}
        onSelect={selectChild}
      />

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
          onClick={handleModoNino}
        >
          Modo niño
        </button>
      </nav>
    </div>
  );
};
