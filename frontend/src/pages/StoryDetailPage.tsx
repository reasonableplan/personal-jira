import { useParams } from "react-router-dom";

export default function StoryDetailPage() {
  const { id } = useParams<{ id: string }>();
  return <div className="p-6"><h1 className="text-2xl font-bold">Story Detail</h1><p>ID: {id}</p></div>;
}
