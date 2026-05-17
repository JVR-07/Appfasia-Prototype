import axios from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const authStateStr = localStorage.getItem("auth-storage");
    if (authStateStr) {
      try {
        const authState = JSON.parse(authStateStr);
        const token = authState.state?.accessToken;
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (e) {
        console.error("Error parsing auth state from localStorage", e);
      }
    }
    return config;
  },
  (error) => Promise.reject(error),
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail || error.message || "Error de conexión";
    return Promise.reject(new Error(message));
  },
);
