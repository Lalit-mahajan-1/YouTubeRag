export interface VideoSummary {
  video_id: string;
  youtube_id: string;
  title: string;
  keywords: string[];
}

export interface Playlist {
  id: string;
  youtube_playlist_id: string;
  youtube_url: string;
  title: string | null;
  total_videos: number;
  video_summaries: VideoSummary[];
  status: "processing" | "ready" | "failed";
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProcessPlaylistResponse {
  message: string;
  playlist: Playlist;
}