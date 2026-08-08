"use client";

import { CheckCircle2, Loader2 } from "lucide-react";

interface StatusItemProps {
  title: string;
  active: boolean;
  completed: boolean;
}

export default function StatusItem({
  title,
  active,
  completed,
}: StatusItemProps) {
  return (
    <div className="flex items-center justify-between bg-[#111827] rounded-xl p-5 border border-white/5">

      <span className="text-white font-medium">
        {title}
      </span>

      {completed ? (
        <CheckCircle2 className="text-green-500" size={22} />
      ) : active ? (
        <Loader2 className="animate-spin text-blue-500" size={22} />
      ) : (
        <div className="w-5 h-5 rounded-full border border-gray-500" />
      )}

    </div>
  );
}