import { apiClient } from "./apiClient";

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface MeResponse {
  id: string;
  nombre: string;
  email: string;
}

export const authService = {
  async register(
    nombre: string,
    email: string,
    password: string,
  ): Promise<{ id_tutor: string; nombre: string; email: string }> {
    const res = await apiClient.post("/auth/register", {
      nombre,
      email,
      password,
    });
    return res.data;
  },

  async login(email: string, password: string): Promise<LoginResponse> {
    const res = await apiClient.post<LoginResponse>("/auth/login", {
      email,
      password,
    });
    return res.data;
  },

  async getMe(): Promise<MeResponse> {
    const res = await apiClient.get<MeResponse>("/auth/me");
    return res.data;
  },
};
