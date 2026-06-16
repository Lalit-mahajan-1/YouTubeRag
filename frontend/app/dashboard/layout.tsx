"use client";

import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import Sidebar from "@/components/dashboard/Sidebar";
import NewChatModal from "@/components/dashboard/NewChatModal";
import { Loader2 } from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isLoading, isAuthenticated } = useAuth(true);
  const [modalOpen, setModalOpen] = useState(false);

  // ⚠️ Show loader while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <Loader2 className="animate-spin text-blue-500" size={32} />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex h-screen bg-gray-900">
      <Sidebar onNewChat={() => setModalOpen(true)} />
      <main className="flex-1 overflow-hidden">{children}</main>
      <NewChatModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
    </div>
  );
}