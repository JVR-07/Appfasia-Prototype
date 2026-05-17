import { create } from "zustand";
import { childrenService, type Child } from "../services/childrenService";
import {
  progressService,
  type ProgressSummary,
} from "../services/progressService";

interface ChildState {
  children: Child[];
  activeChild: Child | null;
  activeProgress: ProgressSummary | null;
  isLoading: boolean;
  error: string | null;

  fetchChildren: () => Promise<void>;
  addChild: (nombre: string, fechaNac: string) => Promise<void>;
  setActiveChild: (child: Child | null) => void;
  loadChildProgress: (childId: string) => Promise<void>;
}

export const useChildStore = create<ChildState>((set, get) => ({
  children: [],
  activeChild: null,
  activeProgress: null,
  isLoading: false,
  error: null,

  fetchChildren: async () => {
    set({ isLoading: true, error: null });
    try {
      const list = await childrenService.listChildren();
      set({ children: list, isLoading: false });

      const { activeChild } = get();
      if (activeChild) {
        const updatedActive = list.find(
          (c) => c.id_child === activeChild.id_child,
        );
        if (updatedActive) {
          set({ activeChild: updatedActive });
        }
      }
    } catch (e: any) {
      set({ error: e.message || "Error al cargar perfiles", isLoading: false });
    }
  },

  addChild: async (nombre, fechaNac) => {
    set({ isLoading: true, error: null });
    try {
      await childrenService.createChild(nombre, fechaNac);
      await get().fetchChildren();
    } catch (e: any) {
      set({ error: e.message || "Error al crear perfil", isLoading: false });
      throw e;
    }
  },

  setActiveChild: (child) => {
    set({ activeChild: child, activeProgress: null });
    if (child) {
      get().loadChildProgress(child.id_child);
    }
  },

  loadChildProgress: async (childId) => {
    try {
      const progress = await progressService.getProgress(childId);
      set({ activeProgress: progress });
    } catch (e: any) {
      console.error("Error al cargar progreso", e);
    }
  },
}));
