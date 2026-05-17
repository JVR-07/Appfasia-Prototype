import React from "react";
import { useNavigate } from "react-router-dom";
import { useChildStore } from "../../store/useChildStore";
import "./Lesson.css";

export const SessionIntro = () => {
  const navigate = useNavigate();
  const { activeChild, activeProgress } = useChildStore();

  if (!activeChild) {
    navigate("/dashboard");
    return null;
  }

  const handleStart = () => {
    navigate("/child/lesson");
  };

  return (
    <div className="lesson-intro-container">
      <div className="lesson-card">
        <h1>¡Hora de jugar, {activeChild.nombre}! 🚀</h1>
        <div className="streak-badge">
          <span className="icon">🔥</span> Racha: {activeChild.racha_dias || 0}{" "}
          días
        </div>
        <p>Tu amigo robot está listo para la lección de hoy.</p>
        <div className="lesson-avatar-placeholder">
          <span style={{ fontSize: "4rem" }}>🤖</span>
        </div>
        <button className="btn-primary start-lesson-btn" onClick={handleStart}>
          ¡Comenzar!
        </button>
        <button
          className="btn-secondary back-btn-lesson"
          onClick={() => navigate("/child/path")}
        >
          Volver
        </button>
      </div>
    </div>
  );
};
