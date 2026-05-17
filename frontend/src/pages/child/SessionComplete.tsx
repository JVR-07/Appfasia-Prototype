import React from "react";
import { useNavigate } from "react-router-dom";
import { useChildStore } from "../../store/useChildStore";
import "./Lesson.css";

export const SessionComplete = () => {
  const navigate = useNavigate();
  const { activeChild } = useChildStore();

  const handleContinue = () => {
    navigate("/child/path");
  };

  return (
    <div className="lesson-intro-container">
      <div className="lesson-card">
        <h1>¡Excelente trabajo, {activeChild?.nombre}! 🌟</h1>
        <p>Has completado todos los ejercicios por hoy.</p>
        <div
          className="lesson-avatar-placeholder"
          style={{ margin: "2rem auto" }}
        >
          <span style={{ fontSize: "5rem" }}>🏆</span>
        </div>
        <button
          className="btn-primary start-lesson-btn"
          onClick={handleContinue}
        >
          Ver mi camino
        </button>
      </div>
    </div>
  );
};
