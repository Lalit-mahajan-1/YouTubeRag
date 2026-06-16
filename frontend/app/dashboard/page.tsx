"use client";

import { MessageSquare, Play } from "lucide-react";

export default function DashboardHome() {
  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-900 px-4">
      <div className="text-center max-w-md">
        <div className="w-16 h-16 mx-auto mb-6 bg-blue-600/20 rounded-2xl flex items-center justify-center">
          <Play className="text-blue-500" size={32} />
        </div>
        <h1 className="text-3xl font-bold text-white mb-3">
          YouTube RAG Chat
        </h1>
        <p className="text-gray-400 mb-6">
          Click <span className="text-blue-500 font-semibold">+ New Chat</span> to
          paste a YouTube URL and start chatting with the video.
        </p>
        <div className="flex items-center gap-2 justify-center text-gray-500 text-sm">
          <MessageSquare size={16} />
          <span>Your chats appear in the sidebar</span>
        </div>
      </div>
    </div>
  );
}