import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useChildStore } from "../../store/useChildStore";
import { diagnosticService } from "../../services/diagnosticService";
import "./Diagnostic.css";

export const DiagnosticResult = () => {
  const navigate = useNavigate();
  const { activeChild } = useChildStore();
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    if (!activeChild) {
      navigate("/dashboard");
      return;
    }

    const loadResult = async () => {
      try {
        const res = await diagnosticService.getResult(activeChild.id_child);
        setResult(res);
      } catch (e) {
        console.error("No se pudo cargar el resultado", e);
      }
    };
    loadResult();
  }, [activeChild, navigate]);

  const handleContinue = () => {
    navigate("/child/path");
  };

  return (
    <div className="diagnostic-intro-container">
      <div className="diagnostic-card">
        <h1>¡Lo hiciste increíble, {activeChild?.nombre}! 🎉</h1>

        <div
          className="diagnostic-avatar-placeholder"
          style={{ margin: "2rem 0" }}
        >
          <span style={{ fontSize: "5rem" }}>🌟</span>
        </div>

        <p style={{ fontSize: "1.2rem", marginBottom: "2rem" }}>
          Ya tengo todo listo para que empecemos a jugar y aprender.
        </p>

        {result && (
          <div className="diagnostic-stats" style={{ display: "none" }}>
            {/* Solo para debugging o si los padres miran de reojo */}
            <small style={{ color: "var(--color-text-muted)" }}>
              Nivel detectado: {result.nivel_detectado} | Interacciones:{" "}
              {result.total_interacciones}
            </small>
          </div>
        )}

        <button className="btn-primary start-diag-btn" onClick={handleContinue}>
          Ver mi camino de aprendizaje
        </button>
      </div>
    </div>
  );
};
