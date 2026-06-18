"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import {
  PanelLeftClose,
  PanelLeftOpen,
  SquarePen,
  Search,
  MessageSquare,
  Trash2,
  LogOut,
  Loader2,
  ListVideo,
} from "lucide-react";
import { toast } from "sonner";
import { chatService } from "@/services/chat.service";
import { useAuthStore } from "@/store/authStore";
import { Chat } from "@/types/chat";
import { getErrorMessage } from "@/lib/helpers";

interface Props {
  onNewChat: () => void;
  collapsed: boolean;
  onToggle: () => void;
}

interface Props {
  onNewChat: () => void;
  onNewPlaylist: () => void; // ✅ NEW
  collapsed: boolean;
  onToggle: () => void;
}

export default function Sidebar({
  onNewChat,
  onNewPlaylist,
  collapsed,
  onToggle,
}: Props) {
  const router = useRouter();
  const params = useParams();
  const { user, logout } = useAuthStore();
  const [chats, setChats] = useState<Chat[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showSearch, setShowSearch] = useState(false);

  const activeChatId = params?.chatId as string;

  useEffect(() => {
    loadChats();
  }, []);

  const loadChats = async () => {
    try {
      const res = await chatService.listChats();
      setChats(res.chats);
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (e: React.MouseEvent, chatId: string) => {
    e.stopPropagation();
    if (!confirm("Delete this chat?")) return;

    try {
      await chatService.deleteChat(chatId);
      setChats((prev) => prev.filter((c) => c.id !== chatId));
      toast.success("Chat deleted");
      if (activeChatId === chatId) router.push("/dashboard");
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  const handleLogout = () => {
    logout();
    router.push("/auth/login");
  };

  const filteredChats = chats.filter((c) =>
    (c.title || "").toLowerCase().includes(search.toLowerCase()),
  );

  // ===== COLLAPSED SIDEBAR =====
  if (collapsed) {
    return (
      <aside className="w-16 h-screen bg-gray-950 border-r border-gray-800 flex flex-col items-center py-3">
        {/* Logo / Toggle */}
        <button
          onClick={onToggle}
          className="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-gray-800 transition mb-2"
          title="Expand sidebar"
        >
          <PanelLeftOpen size={20} className="text-gray-400" />
        </button>

        {/* New Chat */}
        <button
          onClick={onNewChat}
          className="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-gray-800 transition mb-2"
          title="New chat"
        >
          <SquarePen size={20} className="text-gray-300" />
        </button>

        {/* Playlist */}
        <button
          onClick={onNewPlaylist}
          className="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-gray-800 transition mb-2"
          title="New playlist"
        >
          <ListVideo size={20} className="text-purple-400" />
        </button>
        {/* Search */}
        <button
          onClick={() => {
            onToggle();
            setTimeout(() => setShowSearch(true), 200);
          }}
          className="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-gray-800 transition mb-2"
          title="Search chats"
        >
          <Search size={20} className="text-gray-300" />
        </button>

        {/* Chats */}
        <button
          onClick={onToggle}
          className="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-gray-800 transition mb-2"
          title="Chats"
        >
          <MessageSquare size={20} className="text-gray-300" />
        </button>

        {/* Spacer */}
        <div className="flex-1" />

        {/* User Avatar */}
        <button
          onClick={handleLogout}
          className="w-10 h-10 rounded-full bg-red-500 flex items-center justify-center text-white font-semibold text-sm hover:opacity-90 transition"
          title={`${user?.username} — Click to logout`}
        >
          {user?.username?.[0]?.toUpperCase() || "U"}
        </button>
      </aside>
    );
  }

  // ===== EXPANDED SIDEBAR =====
  return (
    <aside className="w-72 h-screen bg-gray-950 border-r border-gray-800 flex flex-col">
      {/* Top Bar */}
      <div className="flex items-center justify-between p-3 border-b border-gray-800/50">
        <span className="text-white font-semibold text-sm px-2">
          YouTube RAG
        </span>
        <button
          onClick={onToggle}
          className="p-2 rounded-lg hover:bg-gray-800 transition"
          title="Collapse sidebar"
        >
          <PanelLeftClose size={18} className="text-gray-400" />
        </button>
      </div>

      {/* Actions */}
      <div className="p-2 space-y-1">
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-800 text-gray-200 text-sm font-medium transition"
        >
          <SquarePen size={16} />
          New chat
        </button>

        <button
          onClick={onNewPlaylist}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-800 text-gray-200 text-sm font-medium transition"
        >
          <ListVideo size={16} className="text-purple-400" />
          New playlist
        </button>
        
        <button
          onClick={() => setShowSearch((v) => !v)}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-800 text-gray-200 text-sm font-medium transition"
        >
          <Search size={16} />
          Search chats
        </button>
      </div>

      {/* Search Input */}
      {showSearch && (
        <div className="px-3 pb-2">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search..."
            autoFocus
            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500"
          />
        </div>
      )}

      {/* Chats */}
      <div className="flex-1 overflow-y-auto px-2">
        <p className="text-xs text-gray-500 px-3 py-2 font-medium">Chats</p>

        {loading ? (
          <div className="flex justify-center py-4">
            <Loader2 className="animate-spin text-gray-500" size={20} />
          </div>
        ) : filteredChats.length === 0 ? (
          <p className="text-gray-500 text-sm px-3 py-2">
            {search ? "No matches" : "No chats yet"}
          </p>
        ) : (
          <div className="space-y-0.5">
            {filteredChats.map((chat) => (
              <div
                key={chat.id}
                onClick={() => router.push(`/dashboard/chat/${chat.id}`)}
                className={`group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition ${
                  activeChatId === chat.id
                    ? "bg-gray-800 text-white"
                    : "text-gray-300 hover:bg-gray-900"
                }`}
              >
                <span className="text-sm truncate flex-1">
                  {chat.title || "Untitled Chat"}
                </span>
                <button
                  onClick={(e) => handleDelete(e, chat.id)}
                  className="opacity-0 group-hover:opacity-100 transition text-gray-500 hover:text-red-500"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* User Footer */}
      <div className="border-t border-gray-800 p-3">
        <div className="flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-gray-800 transition cursor-pointer">
          <div className="w-8 h-8 rounded-full bg-red-500 flex items-center justify-center text-white font-semibold text-sm shrink-0">
            {user?.username?.[0]?.toUpperCase() || "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white text-sm font-medium truncate">
              {user?.username}
            </p>
            <p className="text-gray-500 text-xs truncate">{user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="text-gray-400 hover:text-red-500 transition"
            title="Logout"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
}
