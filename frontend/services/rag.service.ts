import { api } from "@/lib/api";
import { AskQuestionResponse } from "@/types/chat";

export const ragService = {
  ask(chat_id: string, question: string) {
    return api.post<AskQuestionResponse>("/rag/ask", { chat_id, question });
  },
};