import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { MenuIcon } from "lucide-react";

export default function Sortable({ id }: { id: string }) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <li ref={setNodeRef} style={style} {...attributes} {...listeners} className="px-3 py-2 rounded-md cursor-grab flex gap-4 border-2 border-neutral-500">
      <MenuIcon />
      {id.toUpperCase()}
    </li>
  );
}
