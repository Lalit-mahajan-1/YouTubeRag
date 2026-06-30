"use client";

import { useEffect, useState } from "react";
import {
  Loader2,
  Bot,
  Send,
  User as UserIcon,
  Play,
  ExternalLink,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import { toast } from "sonner";
import { playlistService } from "@/services/playlist.service";
import { agentService } from "@/services/agent.service";
import { Playlist } from "@/types/playlist";
import { getErrorMessage } from "@/lib/helpers";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: { video_id: string; video_title: string }[];
}

interface Props {
  playlistId: string;
}

export default function PlaylistView({ playlistId }: Props) {
  const [playlist, setPlaylist] = useState<Playlist | null>(null);
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  useEffect(() => {
    loadPlaylist();
  }, [playlistId]);

  const loadPlaylist = async () => {
    setLoading(true);
    try {
      const data = await playlistService.get(playlistId);
      setPlaylist(data);
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || sending) return;

    const question = input.trim();
    setInput("");
    setSending(true);

    const userMsg: Message = {
      id: `${Date.now()}`,
      role: "user",
      content: question,
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await agentService.ask(playlistId, question);

      const botMsg: Message = {
        id: `${Date.now() + 1}`,
        role: "assistant",
        content: res.answer,
        sources: res.selected_videos,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-900">
        <Loader2 className="animate-spin text-gray-500" size={32} />
      </div>
    );
  }

  if (!playlist) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-900">
        <p className="text-gray-400">Playlist not found</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex h-screen overflow-hidden">
      {/* ===== CENTER: CHAT ===== */}
      <div className="flex-1 flex flex-col bg-gray-900">
        {/* Header */}
        <div className="border-b border-gray-800 p-4 bg-gray-950">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-purple-600/20 rounded-lg flex items-center justify-center shrink-0">
              <Play className="text-purple-500" size={20} />
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-white font-semibold truncate">
                {playlist.title || "Untitled Playlist"}
              </h2>
              <p className="text-xs text-gray-500">
                {playlist.total_videos} videos •{" "}
                <span
                  className={
                    playlist.status === "ready"
                      ? "text-green-400"
                      : playlist.status === "processing"
                      ? "text-yellow-400"
                      : "text-red-400"
                  }
                >
                  {playlist.status}
                </span>
              </p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <Bot className="text-gray-600 mb-3" size={48} />
              <p className="text-white text-lg font-medium">
                Ask anything about this playlist
              </p>
              <p className="text-gray-500 text-sm mt-1">
                Our agent will pick the most relevant videos to answer
              </p>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {msg.role === "assistant" && (
                  <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center shrink-0">
                    <Bot size={16} className="text-white" />
                  </div>
                )}
                <div
                  className={`max-w-2xl rounded-2xl px-4 py-3 ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-800 text-gray-100"
                  }`}
                >
                  <div className="prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>

                  {/* Sources */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-700">
                      <p className="text-xs text-gray-400 mb-2 font-medium">
                        📺 Sources ({msg.sources.length} videos):
                      </p>
                      <div className="space-y-1">
                        {msg.sources.map((src) => (
                          <p
                            key={src.video_id}
                            className="text-xs text-purple-300 truncate"
                          >
                            • {src.video_title}
                          </p>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center shrink-0">
                    <UserIcon size={16} className="text-white" />
                  </div>
                )}
              </div>
            ))
          )}

          {sending && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center shrink-0">
                <Bot size={16} className="text-white" />
              </div>
              <div className="bg-gray-800 rounded-2xl px-4 py-3">
                <Loader2 className="animate-spin text-gray-400" size={16} />
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-gray-800 p-4 bg-gray-950">
          <form onSubmit={handleSend} className="flex gap-2 max-w-4xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about the playlist..."
              disabled={sending}
              className="flex-1 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              className="px-5 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg text-white transition flex items-center gap-2"
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      </div>

      {/* ===== RIGHT: VIDEOS LIST ===== */}
      <aside className="w-80 h-screen bg-gray-950 border-l border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <h3 className="text-white font-semibold text-sm">
            Videos in Playlist
          </h3>
          <p className="text-gray-500 text-xs mt-1">
            {playlist.video_summaries.length} processed
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {playlist.video_summaries.length === 0 ? (
            <p className="text-gray-500 text-sm text-center py-4">
              No videos yet
            </p>
          ) : (
            playlist.video_summaries.map((video, idx) => (
              <div
                key={video.video_id}
                className="bg-gray-900 hover:bg-gray-800 rounded-lg p-3 transition group cursor-pointer"
              >
                <div className="flex items-start gap-2">
                  <span className="text-gray-500 text-xs font-mono mt-0.5 shrink-0">
                    {idx + 1}.
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm font-medium line-clamp-2 mb-2">
                      {video.title}
                    </p>

                    {video.keywords && video.keywords.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-2">
                        {video.keywords.slice(0, 3).map((kw, i) => (
                          <span
                            key={i}
                            className="text-[10px] px-1.5 py-0.5 bg-purple-600/20 text-purple-300 rounded"
                          >
                            {kw}
                          </span>
                        ))}
                      </div>
                    )}

                    <a
                      href={`https://www.youtube.com/watch?v=${video.youtube_id}`}
                      target="_blank"
                      rel="noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
                    >
                      Watch <ExternalLink size={10} />
                    </a>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </aside>
    </div>
  );
}