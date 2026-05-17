import React, { useState, useEffect, useRef } from "react";
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
    if (!inputValue.trim()) return;

    const newUserMsg: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: "user",
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setInputValue("");
    setIsTyping(true);

    // TODO: Aquí se conectará el LLM real.
    // Simulación de respuesta de la IA (Mock)
    setTimeout(() => {
      setIsTyping(false);
      let botResponse = "";

      if (mode === "consejos") {
        botResponse =
          "Es una excelente pregunta. Te sugiero que refuercen jugando con tarjetas de memoria fonéticas antes de dormir. ¿Quieres que te detalle cómo armarlas?";
      } else if (mode === "dudas") {
        botResponse =
          "El nivel 2 introduce fonemas fricativos de forma gradual porque ayuda a desarrollar el control del flujo de aire, lo cual es vital en esta etapa.";
      } else {
        botResponse =
          'He notado que su precisión en los ejercicios de "Sílabas trabadas" mejoró un 40% esta semana. ¡Es un gran avance! Mantuvo una racha perfecta de 3 días.';
      }

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          text: botResponse,
          sender: "bot",
        },
      ]);
    }, 1500);
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
            disabled={isTyping}
          />
          <button
            type="submit"
            className="chat-send-btn"
            disabled={!inputValue.trim() || isTyping}
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
