import { apiClient } from "./apiClient";

export interface DiagnosticStartResponse {
  session_diag_id: string;
  interaccion_num: number;
  max_interacciones: number;
  ejercicio: any;
  avatar_mensaje: string;
}

export interface DiagnosticResponseBody {
  session_diag_id: string;
  tipo_respuesta: "audio" | "seleccion";
  id_seleccionado?: string;
  tra_ms?: number;
  audio_base64?: string;
}

export interface DiagnosticStepResult {
  estado: "EN_CURSO" | "COMPLETADO";
  nivel_detectado?: number;
  resumen?: {
    total_interacciones: number;
    razon: string;
  };
  siguiente_ejercicio?: any;
  interaccion_num?: number;
}

export interface DiagnosticResult {
  nivel_detectado: number;
  total_interacciones: number;
  razon_finalizacion: string;
  created_at: string;
}

export const diagnosticService = {
  async startDiagnostic(childId: string): Promise<DiagnosticStartResponse> {
    const res = await apiClient.post<DiagnosticStartResponse>(
      "/diagnostic/start",
      { child_id: childId },
    );
    return res.data;
  },

  async sendResponse(
    body: DiagnosticResponseBody,
  ): Promise<DiagnosticStepResult> {
    const res = await apiClient.post<DiagnosticStepResult>(
      "/diagnostic/response",
      body,
    );
    return res.data;
  },

  async getResult(childId: string): Promise<DiagnosticResult> {
    const res = await apiClient.get<DiagnosticResult>(
      `/diagnostic/result/${childId}`,
    );
    return res.data;
  },
};
