import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { SessionOrchestrator } from "../../components/Child/Exercises/SessionOrchestrator";
import { useChildStore } from "../../store/useChildStore";
import { diagnosticService } from "../../services/diagnosticService";
import {
  type ActivityInstance,
  type ActivityResult,
} from "../../components/Child/Exercises/types";

export const DiagnosticExam = () => {
  const navigate = useNavigate();
  const { activeChild, loadChildProgress } = useChildStore();

  const [sessionDiagId, setSessionDiagId] = useState<string | null>(null);
  const [initialActivity, setInitialActivity] =
    useState<ActivityInstance | null>(null);
  const [maxInteracciones, setMaxInteracciones] = useState(15);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const startDiag = async () => {
      if (!activeChild) {
        navigate("/dashboard");
        return;
      }

      try {
        const res = await diagnosticService.startDiagnostic(
          activeChild.id_child,
        );
        setSessionDiagId(res.session_diag_id);
        setMaxInteracciones(res.max_interacciones || 15);

        const ejercicioBackend = res.ejercicio;
        const activity: ActivityInstance = {
          id: ejercicioBackend.id_recurso || "ex-start",
          type:
            ejercicioBackend.tipo_interaccion === "seleccion"
              ? "match"
              : "naming",
          title: ejercicioBackend.consigna || "¿Qué es esto?",
          subtitle: res.avatar_mensaje || "Toca el micrófono y responde.",
          targetWord: ejercicioBackend.texto_esperado,
          imageUrl: ejercicioBackend.imagen_url,
          idRecurso: ejercicioBackend.id_recurso,
          options: ejercicioBackend.opciones?.map((o: any) => ({
            id: o.id,
            label: o.texto,
          })),
        };

        setInitialActivity(activity);
      } catch (e: any) {
        setError(e.message || "Error al iniciar diagnóstico");
      } finally {
        setIsLoading(false);
      }
    };

    startDiag();
  }, [activeChild, navigate]);

  const handleExerciseComplete = async (
    result: ActivityResult,
  ): Promise<ActivityInstance | null> => {
    if (!sessionDiagId) return null;

    try {
      const stepRes = await diagnosticService.sendResponse({
        session_diag_id: sessionDiagId,
        tipo_respuesta: result.idSeleccionado ? "seleccion" : "audio",
        id_seleccionado: result.idSeleccionado,
        tra_ms: result.timeTakenMs,
        is_correct: result.isCorrect,
        audio_base64: result.audioBase64 || "",
      });

      if (stepRes.estado === "COMPLETADO") {
        return null;
      }

      if (stepRes.siguiente_ejercicio) {
        const nextEj = stepRes.siguiente_ejercicio;
        return {
          id: nextEj.id_recurso || `ex-${stepRes.interaccion_num}`,
          type: nextEj.tipo_interaccion === "seleccion" ? "match" : "naming",
          title: nextEj.consigna || "Siguiente ejercicio",
          subtitle: "Continuemos",
          targetWord: nextEj.texto_esperado,
          imageUrl: nextEj.imagen_url,
          idRecurso: nextEj.id_recurso,
          options: nextEj.opciones?.map((o: any) => ({
            id: o.id,
            label: o.texto,
          })),
        };
      }

      return null;
    } catch (e) {
      console.error(e);
      throw e;
    }
  };

  const handleSessionComplete = async () => {
    if (activeChild) {
      await loadChildProgress(activeChild.id_child);
    }
    navigate("/child/diagnostic/result");
  };

  if (isLoading) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          backgroundColor: "var(--color-bg)",
        }}
      >
        <h2 style={{ color: "var(--color-primary)" }}>
          Cargando diagnóstico...
        </h2>
      </div>
    );
  }

  if (error || !initialActivity) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          backgroundColor: "var(--color-bg)",
          flexDirection: "column",
        }}
      >
        <h2 style={{ color: "#e53e3e" }}>{error || "Error"}</h2>
        <button
          className="btn btn-primary"
          onClick={() => navigate("/dashboard")}
        >
          Volver
        </button>
      </div>
    );
  }

  return (
    <SessionOrchestrator
      initialActivity={initialActivity}
      totalActivities={maxInteracciones}
      onExerciseComplete={handleExerciseComplete}
      onSessionComplete={handleSessionComplete}
      isDiagnostic={true}
    />
  );
};
