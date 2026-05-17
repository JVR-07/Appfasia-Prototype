import { apiClient } from "./apiClient";

export interface Child {
  id_child: string;
  id_tutor: string;
  nombre: string;
  fecha_nac: string;
  nivel_actual: number | null;
  diagnostico_ok: boolean;
  racha_dias: number;
  created_at: string;
  bkt_summary?: { dominados: number };
}

export const childrenService = {
  async listChildren(): Promise<Child[]> {
    const res = await apiClient.get<Child[]>("/children");
    return res.data;
  },

  async createChild(nombre: string, fecha_nac: string): Promise<Child> {
    const res = await apiClient.post<Child>("/children", { nombre, fecha_nac });
    return res.data;
  },

  async getChild(childId: string): Promise<Child> {
    const res = await apiClient.get<Child>(`/children/${childId}`);
    return res.data;
  },
};
