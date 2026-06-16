import ChatBox from "@/components/dashboard/ChatBox";

interface Props {
  params: Promise<{ chatId: string }>;
}

export default async function ChatPage({ params }: Props) {
  const { chatId } = await params;

  if (!chatId || chatId === "undefined") {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-900">
        <p className="text-gray-400">Invalid chat ID</p>
      </div>
    );
  }

  return <ChatBox chatId={chatId} />;
}