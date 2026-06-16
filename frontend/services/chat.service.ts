import { api } from "@/lib/api";
import {
  Chat,
  ChatHistoryResponse,
  ChatListResponse,
} from "@/types/chat";

export const chatService = {
  createChat(video_id: string, title?: string) {
    return api.post<Chat>("/chat/create", { video_id, title });
  },

  listChats() {
    return api.get<ChatListResponse>("/chat/list");
  },

  getMessages(chat_id: string) {
    return api.get<ChatHistoryResponse>(`/chat/${chat_id}/messages`);
  },

  deleteChat(chat_id: string) {
    return api.delete<void>(`/chat/${chat_id}`);
  },
};