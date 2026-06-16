"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";

export function useAuth(requireAuth: boolean = true) {
  const router = useRouter();
  const { user, isLoading, isAuthenticated, fetchUser } = useAuthStore();
  const fetched = useRef(false);

  useEffect(() => {
    if (!fetched.current) {
      fetched.current = true;
      fetchUser();
    }
  }, [fetchUser]);

  useEffect(() => {
    // ⚠️ CRITICAL: Wait for loading to finish before deciding
    if (isLoading) return;

    if (requireAuth && !isAuthenticated) {
      router.push("/auth/login");
    }

    if (!requireAuth && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isLoading, isAuthenticated, requireAuth, router]);

  return { user, isLoading, isAuthenticated };
}