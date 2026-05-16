import { create } from "zustand";

interface AuthState {
  isAuthenticated: boolean;
  tutorName: string | null;
  tutorId: string | null;
  login: (name: string, id: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  tutorName: null,
  tutorId: null,
  login: (name, id) =>
    set({ isAuthenticated: true, tutorName: name, tutorId: id }),
  logout: () => set({ isAuthenticated: false, tutorName: null, tutorId: null }),
}));
