import { create } from "zustand";
import { User } from "@/types/user";
import { authService } from "@/services/auth.service";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,  // ⚠️ MUST BE TRUE INITIALLY
  isAuthenticated: false,

  login: async (email, password) => {
    set({ isLoading: true });
    try {
      const tokens = await authService.login({ email, password });
      localStorage.setItem("access_token", tokens.access_token);
      localStorage.setItem("refresh_token", tokens.refresh_token);
      const user = await authService.getMe();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (err) {
      set({ isLoading: false });
      throw err;
    }
  },

  register: async (email, username, password) => {
    set({ isLoading: true });
    try {
      await authService.register({ email, username, password });
    } finally {
      set({ isLoading: false });
    }
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ user: null, isAuthenticated: false, isLoading: false });
  },

  fetchUser: async () => {
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;

    if (!token) {
      set({ isLoading: false, user: null, isAuthenticated: false });
      return;
    }

    try {
      const user = await authService.getMe();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      set({ isLoading: false, user: null, isAuthenticated: false });
    }
  },
}));