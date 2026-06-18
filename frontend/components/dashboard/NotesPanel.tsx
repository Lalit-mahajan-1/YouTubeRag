"use client";

import { useEffect, useState } from "react";
import { Download, Loader2, X, FileText } from "lucide-react";
import { toast } from "sonner";
import { notesService } from "@/services/notes.service";
import { getErrorMessage } from "@/lib/helpers";

interface Props {
  videoId: string;
  videoTitle: string;
  onClose: () => void;
}

export default function NotesPanel({ videoId, videoTitle, onClose }: Props) {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [blob, setBlob] = useState<Blob | null>(null);

  useEffect(() => {
    generateNotes();

    return () => {
      if (pdfUrl) URL.revokeObjectURL(pdfUrl);
    };
  }, [videoId]);

  const generateNotes = async () => {
    setLoading(true);
    try {
      const pdfBlob = await notesService.getPdfBlob(videoId);
      const url = URL.createObjectURL(pdfBlob);
      setBlob(pdfBlob);
      setPdfUrl(url);
      toast.success("Notes generated!");
    } catch (err) {
      toast.error(getErrorMessage(err));
      onClose();
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!blob) return;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `notes_${videoTitle.slice(0, 40).replace(/\s+/g, "_")}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success("Downloaded!");
  };

  return (
    <div className="w-1/2 h-screen bg-gray-950 border-l border-gray-800 flex flex-col">
      {/* Header */}
      <div className="flex justify-rightend p-4 border-b border-gray-800">
        <div className="flex items gap-2">
          <FileText className="text-blue-500" size={20} />
          <h2 className="text-white font-semibold">Generated Notes</h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleDownload}
            disabled={!blob || loading}
            className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg text-white text-sm font-medium transition"
          >
            <Download size={16} />
            Download
          </button>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white transition"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* PDF Viewer */}
      <div className="flex-1 overflow-hidden bg-gray-900">
        {loading ? (
          <div className="h-full flex flex-col items-center justify-center text-center px-6">
            <Loader2 className="animate-spin text-blue-500 mb-4" size={40} />
            <p className="text-white font-medium mb-1">Generating notes...</p>
            <p className="text-gray-500 text-sm">
              AI is analyzing the transcript. This may take 10-20 seconds.
            </p>
          </div>
        ) : pdfUrl ? (
          <iframe
            src={pdfUrl}
            className="w-full h-full"
            title="Generated Notes PDF"
          />
        ) : (
          <div className="h-full flex items-center justify-center">
            <p className="text-gray-500">Failed to load PDF</p>
          </div>
        )}
      </div>
    </div>
  );
}