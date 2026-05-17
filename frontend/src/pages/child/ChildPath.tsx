import React from "react";
import { useNavigate } from "react-router-dom";
import "./ChildPath.css";

export const ChildPath = () => {
  const navigate = useNavigate();

  // Simulación de niveles (ruta de aprendizaje)
  const pathNodes = [
    { id: 1, type: "start", title: "Inicio", status: "completed" },
    { id: 2, type: "lesson", title: "Fonema P", status: "completed" },
    { id: 3, type: "lesson", title: "Fonema B", status: "current" },
    { id: 4, type: "chest", title: "Recompensa", status: "locked" },
    { id: 5, type: "lesson", title: "Fonema T", status: "locked" },
    { id: 6, type: "boss", title: "Repaso Final", status: "locked" },
  ];

  const handleGoBack = () => {
    // Para prototipo, regresar al dashboard del tutor
    navigate("/dashboard");
  };

  return (
    <div className="child-path-container">
      {/* Top Header info */}
      <header className="path-header">
        <button className="back-btn" onClick={handleGoBack}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
        </button>

        <div className="path-stats">
          <div className="stat-pill" title="Nivel actual">
            <span className="icon">⭐</span> Nivel 2
          </div>
          <div className="stat-pill" title="Racha de días">
            <span className="icon">🔥</span> 5 Días
          </div>
        </div>
      </header>

      {/* Path Area */}
      <main className="path-scroll-area">
        <div className="path-svg-container">
          {pathNodes.map((node, index) => {
            // Posicionamiento en zigzag básico
            const isLeft = index % 2 === 0;
            const xOffset = isLeft ? "-40px" : "40px";

            return (
              <div key={node.id} className="path-node-wrapper">
                {/* Conector SVG hacia el siguiente nodo (excepto el último) */}
                {index < pathNodes.length - 1 && (
                  <svg
                    className={`path-connector ${isLeft ? "left-to-right" : "right-to-left"}`}
                    viewBox="0 0 80 70"
                  >
                    <path
                      d="M 0,0 C 0,35 80,35 80,70"
                      fill="none"
                      stroke={
                        node.status === "completed" ? "#4ade80" : "#e2e8f0"
                      }
                      strokeWidth="6"
                      strokeLinecap="round"
                      strokeDasharray="12, 12"
                    />
                  </svg>
                )}

                <div
                  style={{
                    transform: `translateX(${xOffset})`,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    position: "relative",
                    zIndex: 2,
                  }}
                >
                  <button
                    className={`path-node ${node.type} ${node.status}`}
                    onClick={() => alert(`Abriendo: ${node.title}`)}
                  >
                    <div className="node-icon">
                      {node.type === "start" && "🚀"}
                      {node.type === "lesson" && "📖"}
                      {node.type === "chest" && "🎁"}
                      {node.type === "boss" && "👑"}
                    </div>
                  </button>
                  <div className="node-title">{node.title}</div>
                </div>
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
};
