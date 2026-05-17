import React from "react";
import { useNavigate } from "react-router-dom";
import { SessionOrchestrator } from "../../components/Child/Exercises/SessionOrchestrator";
import type { ActivityInstance } from "../../components/Child/Exercises/types";

const MOCK_ACTIVITIES: ActivityInstance[] = [
  {
    id: "ex-1",
    type: "naming",
    title: "¿Qué es esto?",
    subtitle: "Toca el micrófono y di el nombre en voz alta.",
    targetWord: "Manzana",
  },
  {
    id: "ex-2",
    type: "repetition",
    title: "Escucha y repite",
    subtitle: "Presiona la bocina, escucha y luego repite.",
    targetWord: "Pa",
  },
  {
    id: "ex-3",
    type: "match",
    title: "Encuentra su pareja",
    subtitle: "Toca la imagen correcta.",
    targetWord: "opt-2",
    imageUrl: "https://via.placeholder.com/150?text=Perro",
    options: [
      { id: "opt-1", label: "Gato" },
      { id: "opt-2", label: "Perro" },
      { id: "opt-3", label: "Pez" },
    ],
  },
];

export const DiagnosticExam = () => {
  const navigate = useNavigate();

  const handleSessionComplete = (results: any) => {
    console.log("Resultados del diagnóstico:", results);
    alert("¡Examen completado! Volviendo a la ruta...");
    navigate("/child/path");
  };

  return (
    <SessionOrchestrator
      activities={MOCK_ACTIVITIES}
      onSessionComplete={handleSessionComplete}
    />
  );
};
