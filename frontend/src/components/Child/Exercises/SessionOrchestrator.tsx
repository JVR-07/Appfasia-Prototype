import React, { useState, useEffect } from "react";
import { NamingExercise } from "./NamingExercise";
import { RepetitionExercise } from "./RepetitionExercise";
import { MatchExercise } from "./MatchExercise";
import "./Exercises.css";

import type { ActivityType, ActivityInstance, ActivityResult } from "./types";

interface SessionOrchestratorProps {
  activities: ActivityInstance[];
  onSessionComplete: (results: ActivityResult[]) => void;
}

export const SessionOrchestrator: React.FC<SessionOrchestratorProps> = ({
  activities,
  onSessionComplete,
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [results, setResults] = useState<ActivityResult[]>([]);
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [attempts, setAttempts] = useState(0);

  useEffect(() => {
    setStartTime(Date.now());
    setAttempts(0);
  }, [currentIndex]);

  const handleComplete = (isCorrect: boolean) => {
    const timeTakenMs = Date.now() - startTime;
    const newResult = {
      activityId: currentActivity.id,
      isCorrect,
      timeTakenMs,
      attempts: attempts + 1,
    };

    setResults((prev) => [...prev, newResult]);

    if (currentIndex < activities.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      onSessionComplete([...results, newResult]);
    }
  };

  const handleFailAttempt = () => {
    setAttempts((prev) => prev + 1);
  };

  if (!activities || activities.length === 0)
    return <div>No hay ejercicios</div>;

  const currentActivity = activities[currentIndex];
  const progress = (currentIndex / activities.length) * 100;

  return (
    <div className="orchestrator-container">
      <header className="orchestrator-header">
        <div className="progress-bar-container">
          <div className="progress-bar-bg">
            <div
              className="progress-bar-fill"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
        <div className="stat-pill">
          Ejercicio {currentIndex + 1} / {activities.length}
        </div>
      </header>

      <main className="orchestrator-main">
        {currentActivity.type === "naming" && (
          <NamingExercise
            activity={currentActivity}
            onSuccess={() => handleComplete(true)}
            onFail={handleFailAttempt}
          />
        )}

        {currentActivity.type === "repetition" && (
          <RepetitionExercise
            activity={currentActivity}
            onSuccess={() => handleComplete(true)}
            onFail={handleFailAttempt}
          />
        )}

        {currentActivity.type === "match" && (
          <MatchExercise
            activity={currentActivity}
            onSuccess={() => handleComplete(true)}
            onFail={handleFailAttempt}
          />
        )}
      </main>
    </div>
  );
};
