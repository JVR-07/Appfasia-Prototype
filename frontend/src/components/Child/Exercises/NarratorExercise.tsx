import React, { useState, useEffect, useRef } from "react";
import type { ActivityInstance } from "./types";

interface NarratorExerciseProps {
  activity: ActivityInstance;
  onSuccess: (transcript: string) => void;
  onFail: () => void;
  feedback?: "correct" | "incorrect" | null;
}

export const NarratorExercise: React.FC<NarratorExerciseProps> = ({
  activity,
  onSuccess,
  onFail,
  feedback,
}) => {
  const [isListening, setIsListening] = useState(false);
  const [micError, setMicError] = useState<string | null>(null);
  const [transcript, setTranscript] = useState("");
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.lang = "es-MX";
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;

      recognitionRef.current.onresult = (event: any) => {
        let currentInterim = "";
        let newFinal = "";

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            newFinal += event.results[i][0].transcript;
          } else {
            currentInterim += event.results[i][0].transcript;
          }
        }

        if (newFinal) {
          setTranscript((prev) => (prev + " " + newFinal).trim());
        }
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error("Speech recognition error", event.error);
        setIsListening(false);
        if (event.error === "not-allowed") {
          setMicError("not-allowed");
        } else if (event.error === "network") {
          setMicError("network");
        } else if (event.error === "no-speech") {
          setMicError("no-speech");
        } else {
          setMicError("error");
        }
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    } else {
      setMicError("no-support");
    }

    return () => {
      if (recognitionRef.current && isListening) {
        recognitionRef.current.stop();
      }
    };
  }, [activity.id]);

  const toggleListen = () => {
    setMicError(null);
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current?.start();
        setIsListening(true);
      } catch (e) {
        console.error("Error al iniciar micrófono:", e);
        setMicError("error");
      }
    }
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    }

    const cleanTranscript = transcript.trim();
    if (cleanTranscript.length > 2) {
      onSuccess(cleanTranscript);
    } else {
      onFail();
      alert("Por favor cuenta un poco más antes de enviar.");
    }
  };

  return (
    <div className={`exercise-card ${feedback || ""}`}>
      <h2 className="exercise-title">{activity.title}</h2>
      <p className="exercise-subtitle">{activity.subtitle}</p>

      <div className="media-container">
        {activity.imageUrl && (
          <img
            src={activity.imageUrl}
            alt="Prompt visual"
            className="exercise-image"
          />
        )}
      </div>

      {activity.targetWord && (
        <div
          style={{
            margin: "-1rem 0 2rem 0",
            fontSize: "1.5rem",
            fontWeight: "bold",
            color: "var(--color-primary)",
            textAlign: "center",
          }}
        >
          Habla sobre:{" "}
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

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "1.5rem",
          width: "100%",
          maxWidth: "600px",
          margin: "0 auto",
        }}
      >
        <textarea
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
          placeholder="Empieza a hablar o escribe tu historia aquí..."
          style={{
            width: "100%",
            minHeight: "100px",
            padding: "1rem",
            borderRadius: "15px",
            border: "3px solid #cbd5e1",
            fontFamily: "inherit",
            fontSize: "1.1rem",
            outline: "none",
            resize: "vertical",
          }}
        />

        <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
          <button
            className={`mic-btn ${isListening ? "listening" : ""}`}
            onClick={toggleListen}
            title={isListening ? "Detener grabación" : "Presiona para hablar"}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="40"
              height="40"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              {isListening ? (
                <rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect>
              ) : (
                <>
                  <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                  <line x1="12" y1="19" x2="12" y2="22"></line>
                </>
              )}
            </svg>
          </button>

          <button
            className="option-btn"
            style={{
              minWidth: "auto",
              margin: 0,
              padding: "0.8rem 2rem",
              backgroundColor: "var(--color-success)",
              color: "white",
              boxShadow: "0 4px 0 #15803d",
              borderColor: "#15803d",
              fontSize: "1.2rem",
              fontWeight: "bold",
            }}
            onClick={() => handleSubmit()}
          >
            Enviar Historia
          </button>
        </div>

        {isListening && (
          <p style={{ color: "var(--color-success)", fontWeight: "bold" }}>
            Escuchando... ¡Empieza a narrar!
          </p>
        )}

        {micError && (
          <div
            style={{
              backgroundColor: "#fffbeb",
              border: "2px solid #fef3c7",
              borderRadius: "15px",
              padding: "1rem",
              width: "100%",
              textAlign: "center",
            }}
          >
            <p
              style={{
                color: "#b45309",
                fontSize: "0.9rem",
                margin: "0 0 0.8rem 0",
                fontWeight: "bold",
              }}
            >
              {micError === "not-allowed"
                ? "🔒 El micrófono está bloqueado por el navegador o requiere HTTPS. Puedes escribir o simular éxito."
                : micError === "network"
                  ? "🌐 Error de red en el reconocimiento de voz. Puedes escribir o simular éxito."
                  : micError === "no-speech"
                    ? "🎙️ No se detectó ninguna voz. Intenta de nuevo acercándote al micrófono. Puedes escribir o simular éxito."
                    : micError === "no-support"
                      ? "⚠️ Tu navegador no soporta el reconocimiento de voz. Puedes escribir o simular éxito."
                      : "❌ Ocurrió un error con el micrófono/reconocimiento. Puedes escribir o simular éxito."}
            </p>
            <div
              style={{
                display: "flex",
                gap: "0.5rem",
                justifyContent: "center",
              }}
            >
              <button
                type="button"
                className="option-btn"
                style={{
                  minWidth: "auto",
                  margin: 0,
                  padding: "0.5rem 1rem",
                  fontSize: "0.9rem",
                  backgroundColor: "#38bdf8",
                  color: "white",
                  borderColor: "#0284c7",
                  boxShadow: "0 4px 0 #0284c7",
                }}
                onClick={() =>
                  onSuccess("Había una vez un perro que jugaba en el parque...")
                }
              >
                ✨ Simular Historia
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
