import React, { useState } from "react";
import "./Chatbot/Chatbot.css";

interface AddChildModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (nombre: string, fechaNac: string) => Promise<void>;
}

export const AddChildModal: React.FC<AddChildModalProps> = ({
  isOpen,
  onClose,
  onAdd,
}) => {
  const [nombre, setNombre] = useState("");
  const [fechaNac, setFechaNac] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      await onAdd(nombre, fechaNac);
      setNombre("");
      setFechaNac("");
      onClose();
    } catch (err: any) {
      setError(err.message || "Error al agregar el perfil.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-modal-overlay open" onClick={onClose}>
      <div
        className="chat-modal"
        onClick={(e) => e.stopPropagation()}
        style={{ height: "auto", maxHeight: "90vh" }}
      >
        <div className="chat-header">
          <h3>👤 Agregar nuevo niño</h3>
          <button
            className="chat-close-btn"
            onClick={onClose}
            disabled={isLoading}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div className="chat-body" style={{ padding: "20px" }}>
          {error && (
            <div
              style={{
                color: "white",
                backgroundColor: "#e53e3e",
                padding: "10px",
                borderRadius: "8px",
                marginBottom: "15px",
              }}
            >
              {error}
            </div>
          )}
          <form
            onSubmit={handleSubmit}
            style={{ display: "flex", flexDirection: "column", gap: "15px" }}
          >
            <div className="form-group" style={{ marginBottom: "0" }}>
              <label className="form-label">Nombre del niño/niña</label>
              <input
                type="text"
                className="form-input"
                placeholder="Ej. Mateo"
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
            <div className="form-group" style={{ marginBottom: "0" }}>
              <label className="form-label">Fecha de Nacimiento</label>
              <input
                type="date"
                className="form-input"
                value={fechaNac}
                onChange={(e) => setFechaNac(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
            <button
              type="submit"
              className="btn btn-primary"
              style={{ marginTop: "10px", width: "100%" }}
              disabled={isLoading}
            >
              {isLoading ? "Agregando..." : "Crear Perfil"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
