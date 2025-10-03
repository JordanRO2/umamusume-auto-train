import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { CircleQuestionMarkIcon } from "lucide-react";

type Props = {
  children: React.ReactNode;
};

export default function Tooltips({ children }: Props) {
  return (
    <Tooltip>
      <TooltipTrigger>
        <CircleQuestionMarkIcon size={20} />
      </TooltipTrigger>
      <TooltipContent>{children}</TooltipContent>
    </Tooltip>
  );
}
