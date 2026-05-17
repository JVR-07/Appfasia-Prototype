import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { authService } from "../services/authService";

interface AuthState {
  isAuthenticated: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  tutorId: string | null;
  tutorName: string | null;
  tutorEmail: string | null;
  login: (email: string, pass: string) => Promise<void>;
  register: (name: string, email: string, pass: string) => Promise<void>;
  logout: () => void;
  hydrate: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      isAuthenticated: false,
      accessToken: null,
      refreshToken: null,
      tutorId: null,
      tutorName: null,
      tutorEmail: null,

      login: async (email, pass) => {
        const data = await authService.login(email, pass);
        set({
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          isAuthenticated: true,
        });

        await get().hydrate();
      },

      register: async (name, email, pass) => {
        await authService.register(name, email, pass);
        await get().login(email, pass);
      },

      logout: () => {
        set({
          isAuthenticated: false,
          accessToken: null,
          refreshToken: null,
          tutorId: null,
          tutorName: null,
          tutorEmail: null,
        });
      },

      hydrate: async () => {
        const { accessToken } = get();
        if (!accessToken) return;

        try {
          const profile = await authService.getMe();
          set({
            tutorId: profile.id,
            tutorName: profile.nombre,
            tutorEmail: profile.email,
            isAuthenticated: true,
          });
        } catch (error) {
          console.error("Token expirado o inválido, auto-logout.");
          get().logout();
        }
      },
    }),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => localStorage),
    },
  ),
);
