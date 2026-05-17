import { apiClient } from "./apiClient";

export interface SessionStartResponse {
  session_id: string;
  child_id: string;
  nivel_sesion: number;
  hito_actual: string | null;
  ejercicio_actual?: any;
  avatar_mensaje: string;
}

export interface SessionResponseBody {
  session_id: string;
  id_actividad: string;
  tipo_respuesta: "audio" | "seleccion";
  audio_base64?: string;
  id_seleccionado?: string;
  texto_esperado?: string;
  id_recurso?: string;
  id_hito?: string;
  plantilla: string;
  tra_ms?: number;
  es_timeout?: boolean;
  transcript?: string;
}

export interface SessionStepResult {
  estado_sesion: "EN_CURSO" | "COMPLETADA";
  decision_motor?: {
    accion: string;
    metricas: any;
    hardware_override?: string;
  };
  next_hito_id?: string;
  siguiente_ejercicio?: any;
  resumen_sesion?: {
    ejercicios_completados: number;
    precision_promedio_ipf: number;
  };
  avatar_mensaje: string;
}

export const sessionService = {
  async startSession(childId: string): Promise<SessionStartResponse> {
    const res = await apiClient.post<SessionStartResponse>("/session/start", {
      child_id: childId,
    });
    return res.data;
  },

  async sendResponse(body: SessionResponseBody): Promise<SessionStepResult> {
    const res = await apiClient.post<SessionStepResult>(
      "/session/response",
      body,
    );
    return res.data;
  },

  async getCurrentSession(childId: string): Promise<any> {
    const res = await apiClient.get(`/session/current/${childId}`);
    return res.data;
  },

  async endSession(sessionId: string): Promise<any> {
    const res = await apiClient.post(`/session/${sessionId}/end`);
    return res.data;
  },
};
