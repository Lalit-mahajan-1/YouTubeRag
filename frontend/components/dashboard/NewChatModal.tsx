"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { X, Loader2, Play } from "lucide-react";
import { toast } from "sonner";
import { youtubeService } from "@/services/youtube.service";
import { chatService } from "@/services/chat.service";
import { getErrorMessage } from "@/lib/helpers";

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export default function NewChatModal({ isOpen, onClose }: Props) {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<"input" | "processing">("input");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setStep("processing");

    try {
      const videoRes = await youtubeService.process(url);
      console.log("📹 Video response:", videoRes);  // 🔍 DEBUG

      const chat = await chatService.createChat(videoRes.video.id);
      console.log("💬 Chat response:", chat);  // 🔍 DEBUG

      if (!chat?.id) {
        throw new Error("Chat ID missing from response");
      }

      toast.success("Video ready! Start chatting.");
      onClose();
      setUrl("");
      setStep("input");
      router.push(`/dashboard/chat/${chat.id}`);
    } catch (err) {
      console.error("❌ Error:", err);
      toast.error(getErrorMessage(err));
      setStep("input");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-800 rounded-2xl w-full max-w-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Play className="text-red-500" size={24} />
            <h2 className="text-white text-xl font-semibold">New Chat</h2>
          </div>
          {!loading && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white"
            >
              <X size={20} />
            </button>
          )}
        </div>

        {step === "input" ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm text-gray-400 mb-2 block">
                YouTube URL
              </label>
              <input
                type="url"
                required
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                autoFocus
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg text-white font-semibold transition"
            >
              Start Chat
            </button>
          </form>
        ) : (
          <div className="py-8 text-center">
            <Loader2 className="animate-spin text-blue-500 mx-auto mb-4" size={40} />
            <p className="text-white font-medium mb-1">Processing video...</p>
            <p className="text-gray-500 text-sm">
              Fetching transcript and creating embeddings.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}