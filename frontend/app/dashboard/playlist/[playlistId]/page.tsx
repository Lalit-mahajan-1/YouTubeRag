import PlaylistView from "@/components/dashboard/PlaylistView";

interface Props {
  params: Promise<{ playlistId: string }>;
}

export default async function PlaylistPage({ params }: Props) {
  const { playlistId } = await params;

  if (!playlistId || playlistId === "undefined") {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-900">
        <p className="text-gray-400">Invalid playlist ID</p>
      </div>
    );
  }

  return <PlaylistView playlistId={playlistId} />;
}