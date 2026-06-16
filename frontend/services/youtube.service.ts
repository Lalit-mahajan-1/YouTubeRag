import { api } from "@/lib/api";
import { ProcessVideoResponse, Video, VideoListResponse } from "@/types/video";

export const youtubeService = {
  process(youtube_url: string) {
    return api.post<ProcessVideoResponse>("/youtube/process", { youtube_url });
  },

  listVideos() {
    return api.get<VideoListResponse>("/youtube/videos");
  },

  getVideo(id: string) {
    return api.get<Video>(`/youtube/videos/${id}`);
  },

  deleteVideo(id: string) {
    return api.delete<void>(`/youtube/videos/${id}`);
  },
};