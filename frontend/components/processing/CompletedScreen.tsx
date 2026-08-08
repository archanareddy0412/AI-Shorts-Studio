"use client";

import { CheckCircle2 } from "lucide-react";

export default function CompletedScreen() {
  return (
    <div className="max-w-3xl mx-auto bg-[#111827] rounded-3xl border border-green-500/20 p-16 text-center">

      <CheckCircle2
        className="mx-auto text-green-500 mb-6"
        size={80}
      />

      <h2 className="text-4xl font-bold text-white">
        Analysis Complete
      </h2>

      <p className="text-gray-400 mt-4">
        Your clips are ready to preview.
      </p>

      <button className="mt-10 bg-blue-600 hover:bg-blue-700 transition px-10 py-4 rounded-xl text-white font-semibold">
        View Generated Clips
      </button>

    </div>
  );
}