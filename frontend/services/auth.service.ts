import { api } from "@/lib/api";
import {
  LoginRequest,
  RegisterRequest,
  RegisterResponse,
  TokenResponse,
  User,
} from "@/types/user";

export const authService = {
  register(data: RegisterRequest) {
    return api.post<RegisterResponse>("/auth/register", data);
  },

  login(data: LoginRequest) {
    return api.post<TokenResponse>("/auth/login", data);
  },

  getMe() {
    return api.get<User>("/auth/me");
  },

  logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },
};