import React, { useState, useEffect, useRef } from "react";
import smallLogo from "../../assets/appfasia-small-logo.svg";
import { ChatModal } from "./ChatModal";
import "./Chatbot.css";

export const ChatbotFab = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeMode, setActiveMode] = useState<
    "consejos" | "dudas" | "resumenes" | null
  >(null);

  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleAction = (event: Event) => {
      if (event.type === "mousedown") {
        const mouseEvent = event as MouseEvent;
        if (
          containerRef.current &&
          !containerRef.current.contains(mouseEvent.target as Node)
        ) {
          setIsMenuOpen(false);
        }
      } else if (event.type === "scroll") {
        setIsMenuOpen(false);
      }
    };

    if (isMenuOpen) {
      document.addEventListener("mousedown", handleAction);
      window.addEventListener("scroll", handleAction, {
        capture: true,
        passive: true,
      });
    }
    return () => {
      document.removeEventListener("mousedown", handleAction);
      window.removeEventListener("scroll", handleAction, { capture: true });
    };
  }, [isMenuOpen]);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const handleOptionClick = (mode: "consejos" | "dudas" | "resumenes") => {
    setActiveMode(mode);
    setIsMenuOpen(false);
    setIsModalOpen(true);
  };

  return (
    <>
      <div className="fab-container" ref={containerRef}>
        <div className={`fab-menu ${isMenuOpen ? "open" : ""}`}>
          <button
            className="fab-menu-item"
            onClick={() => handleOptionClick("consejos")}
          >
            💡 Consejos
          </button>
          <button
            className="fab-menu-item"
            onClick={() => handleOptionClick("dudas")}
          >
            ❓ Resolver Dudas
          </button>
          <button
            className="fab-menu-item"
            onClick={() => handleOptionClick("resumenes")}
          >
            📊 Resumenes
          </button>
        </div>

        <button
          className="fab-button"
          onClick={toggleMenu}
          title="Chatbot Asistente"
        >
          <img src={smallLogo} alt="Chatbot" />
        </button>
      </div>

      <ChatModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        mode={activeMode}
      />
    </>
  );
};
