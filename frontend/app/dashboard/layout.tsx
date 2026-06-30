"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import Sidebar from "@/components/dashboard/Sidebar";
import NewChatModal from "@/components/dashboard/NewChatModal";
import NewPlaylistModal from "@/components/dashboard/NewPlaylistModal";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isLoading, isAuthenticated } = useAuth(true);
  const [chatModalOpen, setChatModalOpen] = useState(false);
  const [playlistModalOpen, setPlaylistModalOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <Loader2 className="animate-spin text-blue-500" size={32} />
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <div className="flex h-screen bg-gray-900">
      <Sidebar
        key={refreshKey}
        onNewChat={() => setChatModalOpen(true)}
        onNewPlaylist={() => setPlaylistModalOpen(true)}
        collapsed={collapsed}
        onToggle={() => setCollapsed((v) => !v)}
      />
      <main className="flex-1 overflow-hidden">{children}</main>

      <NewChatModal
        isOpen={chatModalOpen}
        onClose={() => setChatModalOpen(false)}
      />
      <NewPlaylistModal
        isOpen={playlistModalOpen}
        onClose={() => setPlaylistModalOpen(false)}
        onSuccess={() => setRefreshKey((k) => k + 1)}
      />
    </div>
  );
}