"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { Plus, MessageSquare, LogOut, Trash2, Loader2 } from "lucide-react";
import { chatService } from "@/services/chat.service";
import { useAuthStore } from "@/store/authStore";
import { Chat } from "@/types/chat";
import { toast } from "sonner";
import { getErrorMessage } from "@/lib/helpers";

interface Props {
  onNewChat: () => void;
}

export default function Sidebar({ onNewChat }: Props) {
  const router = useRouter();
  const params = useParams();
  const { user, logout } = useAuthStore();
  const [chats, setChats] = useState<Chat[]>([]);
  const [loading, setLoading] = useState(true);

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

  return (
    <aside className="w-72 h-screen bg-gray-950 border-r border-gray-800 flex flex-col">
      {/* New Chat Button */}
      <div className="p-3">
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition"
        >
          <Plus size={18} />
          New Chat
        </button>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto px-2">
        <p className="text-xs text-gray-500 px-2 py-2 uppercase tracking-wide">
          Recent Chats
        </p>

        {loading ? (
          <div className="flex justify-center py-4">
            <Loader2 className="animate-spin text-gray-500" size={20} />
          </div>
        ) : chats.length === 0 ? (
          <p className="text-gray-500 text-sm px-3 py-2">No chats yet</p>
        ) : (
          <div className="space-y-1">
            {chats.map((chat) => (
              <div
                key={chat.id}
                onClick={() => router.push(`/dashboard/chat/${chat.id}`)}
                className={`group flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer transition ${
                  activeChatId === chat.id
                    ? "bg-gray-800 text-white"
                    : "text-gray-400 hover:bg-gray-900 hover:text-white"
                }`}
              >
                <MessageSquare size={16} className="shrink-0" />
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
        <div className="flex items-center gap-3 px-2 py-2">
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold text-sm">
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