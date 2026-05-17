import { apiClient } from "./apiClient";

export interface ProgressSummary {
  child_id: string;
  nombre: string;
  nivel_actual: number;
  descripcion_nivel: string;
  racha_dias: number;
  resumen_semana: {
    sesiones_completadas: number;
    minutos_totales: number;
    hitos_dominados: number;
  };
  metricas_traducidas: {
    precision_habla: string;
    hitos_dominados_total: number;
  };
  alertas: any[];
}

export interface SessionHistoryItem {
  id_sesion: string;
  fecha_inicio: string;
  estado: string;
  ejercicios_completados: number;
  ipf_promedio: number;
  etiqueta_tutor: string | null;
}

export const progressService = {
  async getProgress(childId: string): Promise<ProgressSummary> {
    const res = await apiClient.get<ProgressSummary>(`/progress/${childId}`);
    return res.data;
  },

  async getSessions(
    childId: string,
    limit = 10,
    offset = 0,
  ): Promise<{ total: number; sessions: SessionHistoryItem[] }> {
    const res = await apiClient.get(`/progress/${childId}/sessions`, {
      params: { limit, offset },
    });
    return res.data;
  },
};
