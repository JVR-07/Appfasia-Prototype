import React, { useState, useEffect } from "react";
import { NamingExercise } from "./NamingExercise";
import { RepetitionExercise } from "./RepetitionExercise";
import { MatchExercise } from "./MatchExercise";
import { ConstructorExercise } from "./ConstructorExercise";
import "./Exercises.css";

import type { ActivityInstance, ActivityResult } from "./types";

interface SessionOrchestratorProps {
  initialActivity: ActivityInstance;
  totalActivities?: number;
  onExerciseComplete: (
    result: ActivityResult,
  ) => Promise<ActivityInstance | null>;
  onSessionComplete?: () => void;
}

export const SessionOrchestrator: React.FC<SessionOrchestratorProps> = ({
  initialActivity,
  totalActivities = 15,
  onExerciseComplete,
  onSessionComplete,
}) => {
  const [currentActivity, setCurrentActivity] =
    useState<ActivityInstance | null>(initialActivity);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [attempts, setAttempts] = useState(0);
  const [isLoadingNext, setIsLoadingNext] = useState(false);

  useEffect(() => {
    setStartTime(Date.now());
    setAttempts(0);
  }, [currentActivity]);

  const handleComplete = async (
    isCorrect: boolean,
    idSeleccionado?: string,
  ) => {
    if (!currentActivity) return;

    const timeTakenMs = Date.now() - startTime;
    const result: ActivityResult = {
      activityId: currentActivity.id,
      isCorrect,
      timeTakenMs,
      attempts: attempts + 1,
      idSeleccionado,
    };

    setIsLoadingNext(true);
    try {
      const nextActivity = await onExerciseComplete(result);
      if (nextActivity) {
        setCurrentActivity(nextActivity);
        setCurrentIndex((prev) => prev + 1);
      } else {
        setCurrentActivity(null);
        if (onSessionComplete) onSessionComplete();
      }
    } catch (e) {
      console.error("Error al obtener siguiente actividad", e);
      alert("Hubo un error al cargar la siguiente actividad.");
    } finally {
      setIsLoadingNext(false);
    }
  };

  const handleFailAttempt = () => {
    setAttempts((prev) => prev + 1);
  };

  if (!currentActivity) {
    return (
      <div
        className="orchestrator-container"
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100%",
        }}
      >
        <h2 style={{ color: "var(--color-primary)" }}>¡Sesión completada!</h2>
      </div>
    );
  }

  const progress = Math.min((currentIndex / totalActivities) * 100, 100);

  return (
    <div className="orchestrator-container">
      <header className="orchestrator-header">
        <div className="progress-bar-container">
          <div className="progress-bar-bg">
            <div
              className="progress-bar-fill"
              style={{
                width: `${progress}%`,
                transition: "width 0.3s ease-in-out",
              }}
            ></div>
          </div>
        </div>
        <div className="stat-pill">
          {isLoadingNext ? "Cargando..." : `Ejercicio ${currentIndex + 1}`}
        </div>
      </header>

      <main
        className="orchestrator-main"
        style={{ opacity: isLoadingNext ? 0.5 : 1, transition: "opacity 0.2s" }}
      >
        {currentActivity.type === "naming" && (
          <NamingExercise
            key={currentActivity.id}
            activity={currentActivity}
            onSuccess={() => handleComplete(true)}
            onFail={handleFailAttempt}
          />
        )}

        {currentActivity.type === "repetition" && (
          <RepetitionExercise
            key={currentActivity.id}
            activity={currentActivity}
            onSuccess={() => handleComplete(true)}
            onFail={handleFailAttempt}
          />
        )}

        {currentActivity.type === "match" && (
          <MatchExercise
            key={currentActivity.id}
            activity={currentActivity}
            onSuccess={(idSelected) => handleComplete(true, idSelected)}
            onFail={handleFailAttempt}
          />
        )}

        {currentActivity.type === "constructor" && (
          <ConstructorExercise
            key={currentActivity.id}
            activity={currentActivity}
            onSuccess={(finalSentence) => handleComplete(true, finalSentence)}
            onFail={handleFailAttempt}
          />
        )}
      </main>
    </div>
  );
};
