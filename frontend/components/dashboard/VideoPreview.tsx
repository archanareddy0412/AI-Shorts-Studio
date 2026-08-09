"use client";

import {
  Play,
  Clock,
  HardDrive,
  Sparkles,
  Loader2,
} from "lucide-react";

import { useState } from "react";

interface VideoPreviewProps {
  file: File;
  onAnalyze: () => void;
  onComplete: () => void;
}

export default function VideoPreview({
  file,
  onAnalyze,
  onComplete,
}: VideoPreviewProps) {
  const size = (file.size / (1024 * 1024)).toFixed(1);

  const [uploading, setUploading] = useState(false);

  async function uploadVideo() {
    try {
      setUploading(true);

      // Show Processing screen immediately
      onAnalyze();

      const formData = new FormData();
      formData.append("file", file);

      // Send video to backend
      const API_URL =
        process.env.NEXT_PUBLIC_API_URL ||
        "http://127.0.0.1:8000";

      const response = await fetch(
        `${API_URL}/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      // Wait for the backend to finish AI processing
      const data = await response.json();

      console.log("Backend result:", data);

      // Backend finished successfully
      if (data.success) {
        onComplete();
      } else {
        throw new Error(
          data.error || "AI processing failed"
        );
      }
    } catch (error) {
      console.error("Processing error:", error);

      alert(
        error instanceof Error
          ? error.message
          : "Upload failed!"
      );
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="bg-[#111827] border border-blue-500/30 rounded-3xl p-8">

      {/* Preview */}
      <div className="aspect-video rounded-2xl bg-black flex items-center justify-center border border-white/10">
        <Play
          size={70}
          className="text-blue-500"
        />
      </div>

      {/* Info */}
      <div className="grid md:grid-cols-3 gap-6 mt-8">

        {/* Filename */}
        <div className="bg-[#0f172a] rounded-xl p-5">
          <p className="text-gray-400 text-sm">
            Filename
          </p>

          <p className="text-white mt-2 font-medium break-all">
            {file.name}
          </p>
        </div>

        {/* File Size */}
        <div className="bg-[#0f172a] rounded-xl p-5">
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <HardDrive size={16} />
            File Size
          </div>

          <p className="text-white mt-2 text-lg">
            {size} MB
          </p>
        </div>

        {/* Status */}
        <div className="bg-[#0f172a] rounded-xl p-5">
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <Clock size={16} />
            Status
          </div>

          <p className="text-green-400 mt-2">
            Ready
          </p>
        </div>

      </div>

      {/* Button */}
      <button
        onClick={uploadVideo}
        disabled={uploading}
        className="mt-10 w-full py-4 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 transition text-white font-semibold flex justify-center items-center gap-3"
      >
        {uploading ? (
          <>
            <Loader2
              className="animate-spin"
              size={20}
            />
            Processing...
          </>
        ) : (
          <>
            <Sparkles size={20} />
            Start AI Analysis
          </>
        )}
      </button>

    </div>
  );
}