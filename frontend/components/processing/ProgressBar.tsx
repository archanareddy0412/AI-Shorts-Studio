"use client";

interface ProgressBarProps {
  progress: number;
}

export default function ProgressBar({
  progress,
}: ProgressBarProps) {
  return (
    <div className="w-full">

      <div className="flex justify-between mb-3">

        <span className="text-gray-400">
          AI Progress
        </span>

        <span className="text-blue-400 font-semibold">
          {progress}%
        </span>

      </div>

      <div className="w-full h-3 rounded-full bg-[#1f2937] overflow-hidden">

        <div
          className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-700"
          style={{ width: `${progress}%` }}
        />

      </div>

    </div>
  );
}