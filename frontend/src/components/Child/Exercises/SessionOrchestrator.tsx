import React, { useState, useEffect } from "react";
import { NamingExercise } from "./NamingExercise";
import { RepetitionExercise } from "./RepetitionExercise";
import { MatchExercise } from "./MatchExercise";
import { ConstructorExercise } from "./ConstructorExercise";
import { NarratorExercise } from "./NarratorExercise";
import "./Exercises.css";

import type { ActivityInstance, ActivityResult } from "./types";

interface SessionOrchestratorProps {
  initialActivity: ActivityInstance;
  totalActivities?: number;
  onExerciseComplete: (
    result: ActivityResult,
  ) => Promise<ActivityInstance | null>;
  onSessionComplete?: () => void;
  isDiagnostic?: boolean;
}

export const SessionOrchestrator: React.FC<SessionOrchestratorProps> = ({
  initialActivity,
  totalActivities = 15,
  onExerciseComplete,
  onSessionComplete,
  isDiagnostic = false,
}) => {
  const [currentActivity, setCurrentActivity] =
    useState<ActivityInstance | null>(initialActivity);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [attempts, setAttempts] = useState(0);
  const [isLoadingNext, setIsLoadingNext] = useState(false);
  const [feedback, setFeedback] = useState<"correct" | "incorrect" | null>(
    null,
  );

  useEffect(() => {
    setStartTime(Date.now());
    setAttempts(0);
  }, [currentActivity]);

  const handleComplete = async (
    isCorrect: boolean,
    idSeleccionado?: string,
    transcript?: string,
  ) => {
    if (!currentActivity) return;

    setFeedback(isCorrect ? "correct" : "incorrect");
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setFeedback(null);

    const timeTakenMs = Date.now() - startTime;
    const result: ActivityResult = {
      activityId: currentActivity.id,
      isCorrect,
      timeTakenMs,
      attempts: attempts + 1,
      idSeleccionado,
      transcript,
      plantilla: currentActivity.plantilla,
      idRecurso: currentActivity.idRecurso,
      idHito: currentActivity.idHito,
      textoEsperado: currentActivity.targetWord,
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

  const handleFailAttempt = (value?: string) => {
    setAttempts((prev) => prev + 1);
    const isAudio =
      currentActivity?.type === "naming" ||
      currentActivity?.type === "repetition";
    handleComplete(
      false,
      isAudio ? undefined : value,
      isAudio ? value : undefined,
    );
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
            onSuccess={(transcript) =>
              handleComplete(true, undefined, transcript)
            }
            onFail={handleFailAttempt}
            feedback={feedback}
          />
        )}

        {currentActivity.type === "repetition" && (
          <RepetitionExercise
            key={currentActivity.id}
            activity={currentActivity}
            onSuccess={(transcript) =>
              handleComplete(true, undefined, transcript)
            }
            onFail={handleFailAttempt}
            feedback={feedback}
          />
        )}

        {currentActivity.type === "match" && (
          <MatchExercise
            key={currentActivity.id}
            activity={currentActivity}
            onSuccess={(idSelected) => handleComplete(true, idSelected)}
            onFail={handleFailAttempt}
            feedback={feedback}
          />
        )}

        {currentActivity.type === "constructor" && (
          <ConstructorExercise
            key={currentActivity.id}
            activity={currentActivity}
            onSuccess={(finalSentence) => handleComplete(true, finalSentence)}
            onFail={() => handleFailAttempt()}
            feedback={feedback}
          />
        )}

        {(currentActivity.type === "narrator" ||
          currentActivity.type === "thinker") && (
          <NarratorExercise
            key={currentActivity.id}
            activity={currentActivity}
            onSuccess={(transcript) =>
              handleComplete(true, undefined, transcript)
            }
            onFail={handleFailAttempt}
            feedback={feedback}
          />
        )}
      </main>
    </div>
  );
};
