import { api } from "@/lib/api";

export interface AgentSource {
  video_id: string;
  video_title: string;
}

export interface AgentAskResponse {
  answer: string;
  selected_videos: AgentSource[];
  total_chunks_used: number;
}

export const agentService = {
  ask(playlist_id: string, question: string) {
    return api.post<AgentAskResponse>("/agent/ask", {
      playlist_id,
      question,
    });
  },
};