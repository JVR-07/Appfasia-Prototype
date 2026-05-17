import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { SessionOrchestrator } from "../../components/Child/Exercises/SessionOrchestrator";
import { useChildStore } from "../../store/useChildStore";
import { sessionService } from "../../services/sessionService";
import type {
  ActivityInstance,
  ActivityResult,
} from "../../components/Child/Exercises/types";

export const LessonPage = () => {
  const navigate = useNavigate();
  const { activeChild, loadChildProgress } = useChildStore();

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [initialActivity, setInitialActivity] =
    useState<ActivityInstance | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const mapTemplateToType = (
    plantilla: string,
  ): "naming" | "repetition" | "match" | "constructor" => {
    switch (plantilla) {
      case "Nombrador":
        return "naming";
      case "Imitador":
        return "repetition";
      case "Identificador":
        return "match";
      case "Constructor":
      case "Ordenador":
        return "constructor";
      default:
        return "naming";
    }
  };

  const mapBackendExercise = (
    ejercicio: any,
    title: string,
    subtitle: string,
  ): ActivityInstance => {
    return {
      id: ejercicio.id_actividad || `ex-${Date.now()}`,
      type: mapTemplateToType(ejercicio.plantilla),
      title: title,
      subtitle: subtitle,
      targetWord: ejercicio.texto_esperado,
      imageUrl: ejercicio.prompt?.imagen_url,
      audioUrl: ejercicio.prompt?.audio_url,
      options: ejercicio.opciones?.map((o: any) => ({
        id: o.id,
        label: o.texto || o.id,
        imageUrl: o.imagen_url,
      })),
    };
  };

  useEffect(() => {
    const startLesson = async () => {
      if (!activeChild) {
        navigate("/dashboard");
        return;
      }

      try {
        const res = await sessionService.startSession(activeChild.id_child);
        setSessionId(res.session_id);

        if (!res.ejercicio_actual) {
          throw new Error("El backend no devolvió el primer ejercicio");
        }

        const activity = mapBackendExercise(
          res.ejercicio_actual,
          "¡Vamos a practicar!",
          res.avatar_mensaje,
        );
        setInitialActivity(activity);
      } catch (e: any) {
        if (
          e.message?.includes("SESSION_LIMIT_REACHED") ||
          e.response?.data?.detail?.error === "SESSION_LIMIT_REACHED"
        ) {
          navigate("/child/lesson/limit");
        } else if (
          e.message?.includes("DIAGNOSTIC_REQUIRED") ||
          e.response?.data?.detail === "DIAGNOSTIC_REQUIRED"
        ) {
          navigate("/child/diagnostic/intro");
        } else {
          setError(e.message || "Error al iniciar sesión");
        }
      } finally {
        setIsLoading(false);
      }
    };

    startLesson();
  }, [activeChild, navigate]);

  const handleExerciseComplete = async (
    result: ActivityResult,
  ): Promise<ActivityInstance | null> => {
    if (!sessionId) return null;

    try {
      const stepRes = await sessionService.sendResponse({
        session_id: sessionId,
        id_actividad: result.activityId,
        tipo_respuesta: result.idSeleccionado ? "seleccion" : "audio",
        id_seleccionado: result.idSeleccionado,
        tra_ms: result.timeTakenMs,
        plantilla: "Practica",
      });

      if (stepRes.estado_sesion === "COMPLETADA") {
        return null;
      }

      if (!stepRes.siguiente_ejercicio) {
        console.warn(
          "El backend no envió el siguiente ejercicio, finalizando por seguridad.",
        );
        return null;
      }

      return mapBackendExercise(
        stepRes.siguiente_ejercicio,
        "¡Sigamos!",
        stepRes.avatar_mensaje,
      );
    } catch (e) {
      console.error(e);
      throw e;
    }
  };

  const handleSessionComplete = async () => {
    if (activeChild) {
      await loadChildProgress(activeChild.id_child);
    }
    navigate("/child/lesson/complete");
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
          Preparando tu lección...
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
          onClick={() => navigate("/child/path")}
        >
          Volver
        </button>
      </div>
    );
  }

  return (
    <SessionOrchestrator
      initialActivity={initialActivity}
      totalActivities={5}
      onExerciseComplete={handleExerciseComplete}
      onSessionComplete={handleSessionComplete}
    />
  );
};
