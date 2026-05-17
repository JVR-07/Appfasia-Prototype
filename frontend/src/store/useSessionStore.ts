import { create } from "zustand";
import {
  sessionService,
  SessionResponseBody,
} from "../services/sessionService";

interface SessionState {
  sessionId: string | null;
  sessionStatus: "idle" | "loading" | "active" | "completed";
  error: string | null;

  startSession: (childId: string) => Promise<any>;
  submitAnswer: (body: SessionResponseBody) => Promise<any>;
  endSession: () => Promise<void>;
  resetSession: () => void;
}

export const useSessionStore = create<SessionState>((set, get) => ({
  sessionId: null,
  sessionStatus: "idle",
  error: null,

  startSession: async (childId: string) => {
    set({ sessionStatus: "loading", error: null });
    try {
      const res = await sessionService.startSession(childId);
      set({ sessionId: res.session_id, sessionStatus: "active" });
      return res;
    } catch (e: any) {
      set({
        sessionStatus: "idle",
        error: e.message || "Error al iniciar sesión",
      });
      throw e;
    }
  },

  submitAnswer: async (body: SessionResponseBody) => {
    try {
      const res = await sessionService.sendResponse(body);
      if (res.estado_sesion === "COMPLETADA") {
        set({ sessionStatus: "completed" });
      }
      return res;
    } catch (e: any) {
      console.error("Error enviando respuesta", e);
      throw e;
    }
  },

  endSession: async () => {
    const { sessionId } = get();
    if (sessionId) {
      try {
        await sessionService.endSession(sessionId);
        set({ sessionStatus: "completed" });
      } catch (e) {
        console.error("Error terminando sesión", e);
      }
    }
  },

  resetSession: () => {
    set({ sessionId: null, sessionStatus: "idle", error: null });
  },
}));
