"use client";

import { useEffect, useRef, useState } from "react";
import {
  Send,
  Loader2,
  Bot,
  User as UserIcon,
  FileText,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import { toast } from "sonner";
import { chatService } from "@/services/chat.service";
import { ragService } from "@/services/rag.service";
import { youtubeService } from "@/services/youtube.service";
import { Message } from "@/types/chat";
import { Video } from "@/types/video";
import { getErrorMessage } from "@/lib/helpers";
import NotesPanel from "./NotesPanel";

interface Props {
  chatId: string;
}

export default function ChatBox({ chatId }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [video, setVideo] = useState<Video | null>(null);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showNotes, setShowNotes] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chatId || chatId === "undefined") {
      setLoading(false);
      return;
    }
    loadChat();
  }, [chatId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadChat = async () => {
    setLoading(true);
    try {
      const history = await chatService.getMessages(chatId);
      setMessages(history.messages);

      const chats = await chatService.listChats();
      const currentChat = chats.chats.find((c) => c.id === chatId);
      if (currentChat) {
        const videoData = await youtubeService.getVideo(currentChat.video_id);
        setVideo(videoData);
      }
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || sending || !chatId) return;

    const question = input.trim();
    setInput("");
    setSending(true);

    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      chat_id: chatId,
      role: "user",
      content: question,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const res = await ragService.ask(chatId, question);

      const assistantMsg: Message = {
        id: res.message_id,
        chat_id: chatId,
        role: "assistant",
        content: res.answer,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      toast.error(getErrorMessage(err));
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMsg.id));
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

  return (
    <div className="flex-1 flex h-screen overflow-hidden">
      {/* ===== LEFT: CHAT ===== */}
      <div
        className={`flex flex-col h-screen bg-gray-900 transition-all ${
          showNotes ? "w-1/2" : "w-full"
        }`}
      >
        {/* Header */}
        {video && (
          <div className="border-b border-gray-800 p-4 bg-gray-950">
            <div className="flex items-start gap-3">
              <div className="w-12 h-12 bg-red-600/20 rounded-lg flex items-center justify-center shrink-0">
                <Bot className="text-red-500" size={20} />
              </div>
              <div className="flex-1 min-w-0">
                <h2 className="text-white font-semibold truncate">
                  {video.title || "YouTube Video"}
                </h2>
                <a
                  href={video.youtube_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-gray-500 hover:text-blue-500 truncate block"
                >
                  {video.youtube_url}
                </a>

                {/* Generate Notes Button */}
                <button
                  onClick={() => setShowNotes(true)}
                  disabled={showNotes}
                  className="mt-3 inline-flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white text-xs font-medium transition"
                >
                  <FileText size={14} />
                  {showNotes ? "Notes Open" : "Generate Notes"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <Bot className="text-gray-600 mb-3" size={48} />
              <p className="text-white text-lg font-medium">
                Ask anything about this video
              </p>
              <p className="text-gray-500 text-sm mt-1">
                I&apos;ll answer based on the transcript
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
                  <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0">
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
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0">
                <Bot size={16} className="text-white" />
              </div>
              <div className="bg-gray-800 rounded-2xl px-4 py-3">
                <Loader2 className="animate-spin text-gray-400" size={16} />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-800 p-4 bg-gray-950">
          <form onSubmit={handleSend} className="flex gap-2 max-w-4xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about the video..."
              disabled={sending}
              className="flex-1 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              className="px-5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg text-white transition flex items-center gap-2"
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      </div>

      {/* ===== RIGHT: NOTES PANEL ===== */}
      {showNotes && video && (
        <NotesPanel
          videoId={video.id}
          videoTitle={video.title || "Notes"}
          onClose={() => setShowNotes(false)}
        />
      )}
    </div>
  );
}