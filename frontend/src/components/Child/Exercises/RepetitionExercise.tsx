import React, { useState, useEffect, useRef } from "react";
import type { ActivityInstance } from "./types";

interface RepetitionExerciseProps {
  activity: ActivityInstance;
  onSuccess: () => void;
  onFail: () => void;
}

export const RepetitionExercise: React.FC<RepetitionExerciseProps> = ({
  activity,
  onSuccess,
  onFail,
}) => {
  const [isListening, setIsListening] = useState(false);
  const [micError, setMicError] = useState<string | null>(null);
  const [typedWord, setTypedWord] = useState("");
  const [showKeyboard, setShowKeyboard] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.lang = "es-MX";
      recognitionRef.current.interimResults = false;
      recognitionRef.current.maxAlternatives = 1;

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript.toLowerCase().trim();
        const target = activity.targetWord.toLowerCase().trim();

        if (transcript.includes(target) || target.includes(transcript)) {
          onSuccess();
        } else {
          onFail();
          alert(
            `Te escuché decir: "${transcript}". Intenta de nuevo decir "${target}".`,
          );
        }
        setIsListening(false);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error("Speech recognition error", event.error);
        setIsListening(false);
        if (event.error === "not-allowed") {
          setMicError("not-allowed");
        } else {
          setMicError("error");
          onFail();
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
  }, [activity.targetWord, onSuccess, onFail]);

  const toggleListen = () => {
    setMicError(null);
    if (isListening) {
      recognitionRef.current?.stop();
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

  const playAudio = () => {
    const utterance = new SpeechSynthesisUtterance(activity.targetWord);
    utterance.lang = "es-MX";
    utterance.rate = 0.8;
    window.speechSynthesis.speak(utterance);
  };

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanTyped = typedWord.toLowerCase().trim();
    const cleanTarget = activity.targetWord.toLowerCase().trim();
    if (cleanTyped === cleanTarget || cleanTarget.includes(cleanTyped)) {
      onSuccess();
    } else {
      onFail();
      alert(`¡Uy! Intentemos de nuevo. Debías repetir "${activity.targetWord}".`);
    }
    setTypedWord("");
  };

  return (
    <div className="exercise-card">
      <h2 className="exercise-title">{activity.title}</h2>
      <p className="exercise-subtitle">{activity.subtitle}</p>

      <div className="media-container">
        <button
          className="audio-btn"
          onClick={playAudio}
          title="Escuchar sonido"
        >
          🔊
        </button>
      </div>

      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "1.5rem" }}>
        {!showKeyboard ? (
          <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
            <button
              className={`mic-btn ${isListening ? "listening" : ""}`}
              onClick={toggleListen}
              title={isListening ? "Escuchando..." : "Presiona para repetir"}
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
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                <line x1="12" y1="19" x2="12" y2="22"></line>
              </svg>
            </button>
            <button 
              className="option-btn"
              style={{ minWidth: "50px", height: "50px", borderRadius: "50%", padding: 0, display: "flex", alignItems: "center", justifyContext: "center", fontSize: "1.2rem", boxShadow: "0 4px 0 #cbd5e1" }}
              onClick={() => setShowKeyboard(true)}
              title="Escribir en lugar de hablar"
            >
              ⌨️
            </button>
          </div>
        ) : (
          <form onSubmit={handleTextSubmit} style={{ display: "flex", gap: "0.5rem", width: "100%", maxWidth: "400px" }}>
            <input 
              type="text" 
              placeholder="Escribe la sílaba/palabra..." 
              value={typedWord}
              onChange={(e) => setTypedWord(e.target.value)}
              style={{
                flex: 1,
                padding: "0.8rem 1.2rem",
                borderRadius: "15px",
                border: "3px solid #cbd5e1",
                fontFamily: "inherit",
                fontSize: "1.1rem",
                outline: "none"
              }}
              autoFocus
            />
            <button type="submit" className="option-btn" style={{ minWidth: "auto", margin: 0, padding: "0.8rem 1.5rem", backgroundColor: "var(--color-success)", color: "white", boxShadow: "0 4px 0 #15803d", borderColor: "#15803d" }}>
              Enviar
            </button>
            <button type="button" className="option-btn" style={{ minWidth: "auto", margin: 0, padding: "0.8rem", backgroundColor: "#94a3b8", color: "white", boxShadow: "0 4px 0 #64748b", borderColor: "#64748b" }} onClick={() => setShowKeyboard(false)}>
              🎤
            </button>
          </form>
        )}

        {isListening && (
          <p style={{ color: "var(--color-success)", fontWeight: "bold" }}>
            Escuchando... ¡Repite ahora!
          </p>
        )}

        {micError && (
          <div style={{
            backgroundColor: "#fffbeb",
            border: "2px solid #fef3c7",
            borderRadius: "15px",
            padding: "1rem",
            maxWidth: "400px",
            textAlign: "center"
          }}>
            <p style={{ color: "#b45309", fontSize: "0.9rem", margin: "0 0 0.8rem 0", fontWeight: "bold" }}>
              {micError === "not-allowed" 
                ? "🔒 El micrófono está bloqueado por el navegador." 
                : "⚠️ Tu navegador no soporta el reconocimiento de voz."}
            </p>
            <div style={{ display: "flex", gap: "0.5rem", justifyContent: "center" }}>
              <button 
                type="button" 
                className="option-btn" 
                style={{ minWidth: "auto", margin: 0, padding: "0.5rem 1rem", fontSize: "0.9rem", boxShadow: "0 4px 0 #cbd5e1" }}
                onClick={() => setShowKeyboard(true)}
              >
                ⌨️ Escribir
              </button>
              <button 
                type="button" 
                className="option-btn" 
                style={{ minWidth: "auto", margin: 0, padding: "0.5rem 1rem", fontSize: "0.9rem", backgroundColor: "#38bdf8", color: "white", borderColor: "#0284c7", boxShadow: "0 4px 0 #0284c7" }}
                onClick={onSuccess}
              >
                ✨ Simular Éxito
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
