import { apiClient } from "./apiClient";

export interface ChatMessageBody {
  child_id: string;
  mensaje: string;
  modo: "consejos" | "dudas" | "resumenes";
  historial: { rol: "user" | "model"; contenido: string }[];
}

export interface ChatbotResponse {
  respuesta: string;
  modelo_usado: string;
  fuente_sugerida: string | null;
}

export const chatbotService = {
  async sendMessage(body: ChatMessageBody): Promise<ChatbotResponse> {
    const res = await apiClient.post<ChatbotResponse>("/chatbot/message", body);
    return res.data;
  },
};
