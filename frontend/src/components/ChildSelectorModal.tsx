import React from "react";
import type { Child } from "../services/childrenService";

interface ChildSelectorModalProps {
  isOpen: boolean;
  onClose: () => void;
  childrenList: Child[];
  onSelect: (child: Child) => void;
}

export const ChildSelectorModal: React.FC<ChildSelectorModalProps> = ({
  isOpen,
  onClose,
  childrenList,
  onSelect,
}) => {
  if (!isOpen) return null;

  return (
    <div className="chat-modal-overlay open" onClick={onClose}>
      <div
        className="chat-modal"
        onClick={(e) => e.stopPropagation()}
        style={{ height: "auto", maxHeight: "90vh" }}
      >
        <div className="chat-header">
          <h3>🎮 ¿Quién va a jugar hoy?</h3>
          <button className="chat-close-btn" onClick={onClose}>
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
        <div
          className="chat-body"
          style={{
            padding: "20px",
            display: "flex",
            flexWrap: "wrap",
            gap: "15px",
            justifyContent: "center",
          }}
        >
          {childrenList.map((child) => (
            <div
              key={child.id_child}
              style={{
                background: "var(--color-bg)",
                border: "2px solid #E2E8F0",
                borderRadius: "16px",
                padding: "15px",
                cursor: "pointer",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                width: "140px",
                transition: "transform 0.2s, borderColor 0.2s",
              }}
              onClick={() => onSelect(child)}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-5px)";
                e.currentTarget.style.borderColor = "var(--color-primary)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.borderColor = "#E2E8F0";
              }}
            >
              <img
                src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${child.id_child}&backgroundColor=f1f5f9`}
                alt={child.nombre}
                style={{
                  width: "80px",
                  height: "80px",
                  borderRadius: "50%",
                  marginBottom: "10px",
                }}
              />
              <h4
                style={{ margin: "0 0 5px 0", color: "var(--color-text-main)" }}
              >
                {child.nombre}
              </h4>
              <span
                style={{
                  fontSize: "0.85rem",
                  color: "var(--color-text-muted)",
                }}
              >
                {child.diagnostico_ok ? `Nivel ${child.nivel_actual}` : "Nuevo"}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
