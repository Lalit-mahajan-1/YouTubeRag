const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const notesService = {
  async getPdfBlob(videoId: string): Promise<Blob> {
    const token = localStorage.getItem("access_token");

    const res = await fetch(`${API_BASE_URL}/api/notes/${videoId}/pdf`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw { response: { status: res.status, data } };
    }

    return res.blob();
  },
};