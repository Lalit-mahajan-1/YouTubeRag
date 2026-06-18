import { api } from "@/lib/api";
import { Playlist, ProcessPlaylistResponse } from "@/types/playlist";

export const playlistService = {
  process(youtube_url: string) {
    return api.post<ProcessPlaylistResponse>("/playlist/process", {
      youtube_url,
    });
  },

  list() {
    return api.get<{ total: number; playlists: Playlist[] }>("/playlist/list");
  },

  get(id: string) {
    return api.get<Playlist>(`/playlist/${id}`);
  },

  delete(id: string) {
    return api.delete<void>(`/playlist/${id}`);
  },
};