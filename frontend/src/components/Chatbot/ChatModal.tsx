import React, { useState, useEffect, useRef } from "react";
import { useChildStore } from "../../store/useChildStore";
import { chatbotService } from "../../services/chatbotService";
import "./Chatbot.css";

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
}

interface ChatModalProps {
  isOpen: boolean;
  onClose: () => void;
  mode: "consejos" | "dudas" | "resumenes" | null;
}

export const ChatModal: React.FC<ChatModalProps> = ({
  isOpen,
  onClose,
  mode,
}) => {
  const { activeChild } = useChildStore();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  useEffect(() => {
    if (isOpen && mode && messages.length === 0) {
      let initialMsg = "";
      if (mode === "consejos") {
        initialMsg =
          "¡Hola! Soy tu asistente Appfasia. ¿Sobre qué área te gustaría recibir consejos para apoyar a tu pequeño en casa hoy?";
      } else if (mode === "dudas") {
        initialMsg =
          "¡Hola! Estoy aquí para resolver cualquier duda que tengas sobre la aplicación, los niveles o los ejercicios. ¿En qué te ayudo?";
      } else if (mode === "resumenes") {
        initialMsg =
          "¡Hola! He estado analizando el progreso reciente. ¿Te gustaría un resumen general o datos curiosos sobre alguna lección específica?";
      }

      setMessages([
        { id: Date.now().toString(), text: initialMsg, sender: "bot" },
      ]);
    }

    if (!isOpen) {
      setTimeout(() => {
        setMessages([]);
      }, 300);
    }
  }, [isOpen, mode]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputValue.trim() || !activeChild || !mode) return;

    const userText = inputValue.trim();
    const newUserMsg: Message = {
      id: Date.now().toString(),
      text: userText,
      sender: "user",
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setInputValue("");
    setIsTyping(true);

    try {
      const historial = messages.map((m) => ({
        rol: m.sender === "user" ? "user" : "model",
        contenido: m.text,
      }));

      const res = await chatbotService.sendMessage({
        child_id: activeChild.id_child,
        mensaje: userText,
        modo: mode,
        historial: historial,
      });

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          text: res.respuesta,
          sender: "bot",
        },
      ]);
    } catch (error) {
      console.error("Error al comunicarse con el chatbot:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          text: "Lo siento, tuve un problema al procesar tu solicitud. Por favor intenta nuevamente.",
          sender: "bot",
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const getTitle = () => {
    switch (mode) {
      case "consejos":
        return "💡 Consejos del Asistente";
      case "dudas":
        return "❓ Resolver Dudas";
      case "resumenes":
        return "📊 Resumen del Progreso";
      default:
        return "🤖 Asistente Appfasia";
    }
  };

  return (
    <div
      className={`chat-modal-overlay ${isOpen ? "open" : ""}`}
      onClick={onClose}
    >
      <div className="chat-modal" onClick={(e) => e.stopPropagation()}>
        <div className="chat-header">
          <h3>{getTitle()}</h3>
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

        <div className="chat-body">
          {!activeChild && (
            <div
              style={{
                textAlign: "center",
                color: "#e53e3e",
                marginBottom: "15px",
                padding: "10px",
                background: "#fef2f2",
                borderRadius: "8px",
              }}
            >
              Por favor, selecciona un niño en el panel primero.
            </div>
          )}
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`message-bubble ${msg.sender === "user" ? "message-user" : "message-bot"}`}
            >
              {msg.text}
            </div>
          ))}
          {isTyping && (
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="chat-footer" onSubmit={handleSend}>
          <input
            type="text"
            className="chat-input"
            placeholder="Escribe tu mensaje..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isTyping || !activeChild}
          />
          <button
            type="submit"
            className="chat-send-btn"
            disabled={!inputValue.trim() || isTyping || !activeChild}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
};
