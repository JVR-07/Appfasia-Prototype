import React from "react";
import { useNavigate } from "react-router-dom";
import { useChildStore } from "../../store/useChildStore";
import "./Diagnostic.css";

export const DiagnosticIntro = () => {
  const navigate = useNavigate();
  const { activeChild } = useChildStore();

  if (!activeChild) {
    navigate("/dashboard");
    return null;
  }

  const handleStart = () => {
    navigate("/child/diagnostic/exam");
  };

  return (
    <div className="diagnostic-intro-container">
      <div className="diagnostic-card">
        <h1>¡Hola, {activeChild.nombre}! 👋</h1>
        <p>
          Vamos a jugar un ratito para conocerte mejor. <br />
          No te preocupes si no sabes alguna respuesta, ¡estamos aquí para
          aprender juntos!
        </p>
        <div className="diagnostic-avatar-placeholder">
          {/* Aquí iría una animación o imagen del avatar saludando */}
          <span style={{ fontSize: "4rem" }}>🤖</span>
        </div>
        <button className="btn-primary start-diag-btn" onClick={handleStart}>
          ¡Empezar a jugar!
        </button>
      </div>
    </div>
  );
};
