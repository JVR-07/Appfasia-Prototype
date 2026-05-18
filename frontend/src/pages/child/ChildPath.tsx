import React from "react";
import { useNavigate } from "react-router-dom";
import { useChildStore } from "../../store/useChildStore";
import "./ChildPath.css";

export const ChildPath = () => {
  const navigate = useNavigate();
  const { activeChild, activeProgress } = useChildStore();

  const buildDynamicNodes = () => {
    const defaultNodes = [
      { id: 1, type: "start", title: "Inicio", status: "completed" },
      { id: 2, type: "lesson", title: "Lección Diaria", status: "current" },
    ];

    if (!activeProgress) return defaultNodes;

    const sesiones = activeProgress.resumen_semana?.sesiones_completadas || 0;

    const nodes = [
      { id: 1, type: "start", title: "Inicio", status: "completed" },
    ];

    for (let i = 0; i < sesiones; i++) {
      nodes.push({
        id: 2 + i,
        type: "lesson",
        title: `Lección ${i + 1}`,
        status: "completed",
      });
    }

    if (sesiones >= 2) {
      nodes.push({
        id: nodes.length + 1,
        type: "chest",
        title: "¡Recompensa!",
        status: "completed",
      });
    }

    nodes.push({
      id: nodes.length + 1,
      type: "lesson",
      title: "Hoy",
      status: "current",
    });

    nodes.push({
      id: nodes.length + 1,
      type: "chest",
      title: "Sorpresa",
      status: "locked",
    });
    nodes.push({
      id: nodes.length + 1,
      type: "boss",
      title: "Repaso",
      status: "locked",
    });

    return nodes;
  };

  const pathNodes = buildDynamicNodes();

  const handleGoBack = () => {
    navigate("/dashboard");
  };

  const handleNodeClick = (node: any) => {
    if (node.status === "current") {
      navigate("/child/lesson/intro");
    } else if (node.status === "completed") {
      alert("Ya completaste esta lección.");
    } else {
      alert("Debes completar la lección actual primero.");
    }
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
            <span className="icon">⭐</span> Nivel{" "}
            {activeChild?.nivel_actual || 1}
          </div>
          <div className="stat-pill" title="Racha de días">
            <span className="icon">🔥</span> {activeChild?.racha_dias || 0} Días
          </div>
        </div>
      </header>

      {/* Path Area */}
      <main className="path-scroll-area">
        <div className="path-svg-container">
          {pathNodes.map((node, index) => {
            const isLeft = index % 2 === 0;
            const xOffset = isLeft ? "-40px" : "40px";

            return (
              <div key={node.id} className="path-node-wrapper">
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
                    onClick={() => handleNodeClick(node)}
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
