import { apiClient } from "./apiClient";

export interface Publication {
  id: string;
  titulo: string;
  resumen: string;
  contenido: string;
  tags: string[];
  imagen_url: string | null;
  created_at: string;
  tiempo?: string;
}

export const publicationsService = {
  async getPublications(since?: string): Promise<Publication[]> {
    const url = since
      ? `/publications?since=${encodeURIComponent(since)}`
      : "/publications";
    const res = await apiClient.get<Publication[]>(url);
    return res.data;
  },

  async syncPublications(): Promise<Publication[]> {
    const CACHE_KEY = "appfasia_pubs_cache";
    const LAST_SYNC_KEY = "appfasia_pubs_last_sync";

    let cachedPubs: Publication[] = [];
    try {
      const stored = localStorage.getItem(CACHE_KEY);
      if (stored) cachedPubs = JSON.parse(stored);
    } catch (e) {
      console.error("Error parseando cache de pubs");
    }

    const lastSync = localStorage.getItem(LAST_SYNC_KEY) || undefined;

    try {
      const newPubs = await this.getPublications(lastSync);

      if (newPubs.length > 0) {
        const merged = [...newPubs, ...cachedPubs].sort(
          (a, b) =>
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
        );

        localStorage.setItem(CACHE_KEY, JSON.stringify(merged));
        localStorage.setItem(LAST_SYNC_KEY, new Date().toISOString());
        return merged;
      }

      return cachedPubs;
    } catch (e) {
      console.error("Error sincronizando publicaciones, usando cache.", e);
      return cachedPubs;
    }
  },
};
