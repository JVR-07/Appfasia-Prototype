import React from "react";
import { useNavigate } from "react-router-dom";
import { useChildStore } from "../../store/useChildStore";
import "./Lesson.css";

export const DailyLimit = () => {
  const navigate = useNavigate();
  const { activeChild } = useChildStore();

  const handleContinue = () => {
    navigate("/child/path");
  };

  return (
    <div className="lesson-intro-container">
      <div className="lesson-card">
        <h1>¡Descansa un poco, {activeChild?.nombre}! 💤</h1>
        <p>Ya completaste tu sesión de hoy. ¡Lo hiciste muy bien!</p>
        <p>Vuelve mañana para seguir aprendiendo.</p>
        <div
          className="lesson-avatar-placeholder"
          style={{ margin: "2rem auto" }}
        >
          <span style={{ fontSize: "5rem" }}>📅</span>
        </div>
        <button
          className="btn-secondary back-btn-lesson"
          onClick={handleContinue}
          style={{ width: "100%", marginTop: "1rem" }}
        >
          Ver mi camino
        </button>
      </div>
    </div>
  );
};
