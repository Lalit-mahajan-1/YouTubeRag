"use client";

import { useState } from "react";
import { X, Loader2, ListVideo } from "lucide-react";
import { toast } from "sonner";
import { playlistService } from "@/services/playlist.service";
import { getErrorMessage } from "@/lib/helpers";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export default function NewPlaylistModal({ isOpen, onClose, onSuccess }: Props) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    try {
      const res = await playlistService.process(url);
      toast.success(
        `Playlist processed! ${res.playlist.video_summaries.length} videos ready.`
      );
      onClose();
      setUrl("");
      onSuccess?.();
    } catch (err) {
      toast.error(getErrorMessage(err));
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
            <ListVideo className="text-purple-500" size={24} />
            <h2 className="text-white text-xl font-semibold">New Playlist</h2>
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

        {!loading ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm text-gray-400 mb-2 block">
                YouTube Playlist URL
              </label>
              <input
                type="url"
                required
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.youtube.com/playlist?list=..."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
                autoFocus
              />
              <p className="text-xs text-gray-500 mt-2">
                All videos will be processed and added to your library.
              </p>
            </div>

            <button
              type="submit"
              className="w-full py-3 bg-purple-600 hover:bg-purple-700 rounded-lg text-white font-semibold transition"
            >
              Process Playlist
            </button>
          </form>
        ) : (
          <div className="py-8 text-center">
            <Loader2
              className="animate-spin text-purple-500 mx-auto mb-4"
              size={40}
            />
            <p className="text-white font-medium mb-1">Processing playlist...</p>
            <p className="text-gray-500 text-sm">
              Fetching videos and creating embeddings. This may take a few minutes.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}