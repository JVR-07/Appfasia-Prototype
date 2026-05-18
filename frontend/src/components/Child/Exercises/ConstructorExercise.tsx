import React, { useState } from "react";
import type { ActivityInstance } from "./types";

interface ConstructorExerciseProps {
  activity: ActivityInstance;
  onSuccess: (resultadoFinal: string) => void;
  onFail: () => void;
  isDiagnostic?: boolean;
  feedback?: "correct" | "incorrect" | null;
}

export const ConstructorExercise: React.FC<ConstructorExerciseProps> = ({
  activity,
  onSuccess,
  onFail,
  feedback,
}) => {
  const generateWords = () => {
    if (activity.options && activity.options.length > 0) {
      return activity.options.map((o) => o.label);
    }
    const target = activity.targetWord || "";
    if (target.includes(" ")) {
      return target.split(" ").sort(() => Math.random() - 0.5);
    } else {
      return target.split("").sort(() => Math.random() - 0.5);
    }
  };

  const words = React.useMemo(() => generateWords(), [activity.id]);
  const [selectedWords, setSelectedWords] = useState<string[]>([]);
  const [availableWords, setAvailableWords] = useState<string[]>(words);

  // Reset state when activity changes
  React.useEffect(() => {
    setSelectedWords([]);
    setAvailableWords(generateWords());
  }, [activity.id]);

  const handleSelect = (word: string) => {
    setSelectedWords([...selectedWords, word]);
    setAvailableWords(availableWords.filter((w) => w !== word));
  };

  const handleDeselect = (word: string) => {
    setAvailableWords([...availableWords, word]);
    setSelectedWords(selectedWords.filter((w) => w !== word));
  };

  const handleCheck = () => {
    const finalSentence = selectedWords.join(activity.targetWord?.includes(" ") ? " " : "");
    if (finalSentence === activity.targetWord) {
      onSuccess(finalSentence);
    } else {
      onFail();
      // Reset
      setSelectedWords([]);
      setAvailableWords(words);
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
            alt="Ordena"
            className="exercise-image"
            style={{ maxHeight: "150px" }}
          />
        ) : (
          <div className="exercise-image" style={{ fontSize: "4rem" }}>
            🧩
          </div>
        )}
      </div>

      <div
        style={{
          margin: "-1rem 0 1rem 0",
          fontSize: "1.2rem",
          fontWeight: "bold",
          color: "var(--color-primary)",
        }}
      >
        Selecciona las piezas en el orden correcto:
      </div>

      <div
        className="constructor-area"
        style={{
          minHeight: "60px",
          borderBottom: "2px dashed #cbd5e1",
          marginBottom: "2rem",
          padding: "1rem",
          display: "flex",
          gap: "0.5rem",
          flexWrap: "wrap",
        }}
      >
        {selectedWords.map((word, idx) => (
          <button
            key={`sel-${idx}`}
            className="option-btn"
            style={{
              padding: "0.5rem 1rem",
              background: "var(--color-primary)",
              color: "white",
            }}
            onClick={() => handleDeselect(word)}
          >
            {word}
          </button>
        ))}
      </div>

      <div
        className="options-grid"
        style={{ gridTemplateColumns: "repeat(auto-fit, minmax(100px, 1fr))" }}
      >
        {availableWords.map((word, idx) => (
          <button
            key={`avail-${idx}`}
            className="option-btn"
            style={{ padding: "0.5rem 1rem" }}
            onClick={() => handleSelect(word)}
          >
            {word}
          </button>
        ))}
      </div>

      {selectedWords.length > 0 && availableWords.length === 0 && (
        <button
          className="btn-primary"
          style={{ width: "100%", marginTop: "2rem" }}
          onClick={handleCheck}
        >
          Revisar
        </button>
      )}
    </div>
  );
};
