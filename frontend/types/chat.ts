export interface Message {
  id: string;
  chat_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface Chat {
  id: string;
  video_id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatListResponse {
  total: number;
  chats: Chat[];
}

export interface ChatHistoryResponse {
  chat_id: string;
  messages: Message[];
}

export interface AskQuestionResponse {
  answer: string;
  chat_id: string;
  message_id: string;
  sources?: { content: string; score: number | null }[];
}