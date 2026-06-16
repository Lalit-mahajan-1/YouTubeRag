"use client";

import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";

export default function HomePage() {
  const { isAuthenticated, isLoading } = useAuth(false);

  if (isLoading) return null;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-950">
      <h1 className="text-5xl font-bold text-white mb-4">YouTube RAG</h1>
      <p className="text-gray-400 text-lg mb-8">
        Chat with any YouTube video using AI
      </p>
      <div className="flex gap-4">
        <Link
          href="/auth/login"
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-semibold transition"
        >
          Login
        </Link>
        <Link
          href="/auth/register"
          className="px-6 py-3 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-white font-semibold transition"
        >
          Register
        </Link>
      </div>
    </div>
  );
}