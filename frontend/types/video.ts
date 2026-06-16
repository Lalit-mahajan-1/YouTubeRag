export interface Video {
  id: string;
  youtube_id: string;
  youtube_url: string;
  title: string | null;
  thumbnail_url: string | null;
  duration: number | null;
  status: "processing" | "ready" | "failed";
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface VideoListResponse {
  total: number;
  videos: Video[];
}

export interface ProcessVideoResponse {
  message: string;
  video: Video;
}