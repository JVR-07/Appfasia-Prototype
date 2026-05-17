import React from "react";
import type { ActivityInstance } from "./types";

interface MatchExerciseProps {
  activity: ActivityInstance;
  onSuccess: (idSeleccionado: string) => void;
  onFail: () => void;
}

export const MatchExercise: React.FC<MatchExerciseProps> = ({
  activity,
  onSuccess,
  onFail,
}) => {
  const handleOptionClick = (optionId: string) => {
    if (optionId === activity.targetWord) {
      onSuccess(optionId);
    } else {
      onFail();
      alert("¡Uy! Esa no es. Intenta de nuevo.");
    }
  };

  return (
    <div className="exercise-card">
      <h2 className="exercise-title">{activity.title}</h2>
      <p className="exercise-subtitle">{activity.subtitle}</p>

      <div className="media-container">
        {activity.imageUrl ? (
          <img
            src={activity.imageUrl}
            alt="Encuentra"
            className="exercise-image"
          />
        ) : activity.audioUrl ? (
          <button
            className="audio-btn"
            onClick={() => {
              const utterance = new SpeechSynthesisUtterance(
                "Encuentra la opción correcta",
              );
              window.speechSynthesis.speak(utterance);
            }}
          >
            🔊
          </button>
        ) : (
          <div className="exercise-image" style={{ fontSize: "4rem" }}>
            ❓
          </div>
        )}
      </div>

      <div className="options-grid">
        {activity.options?.map((opt) => (
          <button
            key={opt.id}
            className="option-btn"
            onClick={() => handleOptionClick(opt.id)}
          >
            {opt.imageUrl ? (
              <img
                src={opt.imageUrl}
                alt={opt.label}
                style={{ width: "100px", height: "100px" }}
              />
            ) : (
              opt.label
            )}
          </button>
        ))}
      </div>
    </div>
  );
};
