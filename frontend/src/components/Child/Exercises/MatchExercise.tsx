import React from "react";
import type { ActivityInstance } from "./types";

interface MatchExerciseProps {
  activity: ActivityInstance;
  onSuccess: (idSeleccionado: string) => void;
  onFail: (idSeleccionado?: string) => void;
  isDiagnostic?: boolean;
  feedback?: "correct" | "incorrect" | null;
}

export const MatchExercise: React.FC<MatchExerciseProps> = ({
  activity,
  onSuccess,
  onFail,
  feedback,
}) => {
  const handleOptionClick = (optionId: string) => {
    const isCorrect =
      optionId === activity.idRecurso ||
      optionId === activity.targetWord ||
      optionId === activity.id;
    if (isCorrect) {
      onSuccess(optionId);
    } else {
      onFail(optionId);
    }
  };

  return (
    <div className={`exercise-card ${feedback || ""}`}>
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
                activity.targetWord,
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

      {!activity.imageUrl && activity.audioUrl && (
        <div
          style={{
            margin: "-1rem 0 2rem 0",
            fontSize: "1.6rem",
            fontWeight: "bold",
            color: "var(--color-primary)",
            textAlign: "center",
          }}
        >
          Selecciona la palabra:{" "}
          <span
            style={{
              textDecoration: "underline",
              color: "var(--color-success)",
            }}
          >
            "{activity.targetWord}"
          </span>
        </div>
      )}

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
