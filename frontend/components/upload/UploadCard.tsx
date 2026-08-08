"use client";

import { UploadCloud } from "lucide-react";
import { useRef, useState } from "react";

import VideoPreview from "../dashboard/VideoPreview";
import ProcessingScreen from "../processing/ProcessingScreen";
import CompletedScreen from "../processing/CompletedScreen";

export default function UploadCard() {
  const inputRef = useRef<HTMLInputElement>(null);

  const [video, setVideo] = useState<File | null>(null);

  const [screen, setScreen] = useState<
    "upload" | "preview" | "processing" | "completed"
  >("upload");

  function selectFile() {
    inputRef.current?.click();
  }

  function onFileChange(
    e: React.ChangeEvent<HTMLInputElement>
  ) {
    if (!e.target.files || e.target.files.length === 0) {
      return;
    }

    const file = e.target.files[0];

    setVideo(file);
    setScreen("preview");
  }

  return (
    <>
      {/* Hidden file input */}
      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        hidden
        onChange={onFileChange}
      />

      {/* Upload screen */}
      {screen === "upload" && (
        <div
          onClick={selectFile}
          className="cursor-pointer border-2 border-dashed border-blue-500 rounded-2xl h-96 flex flex-col justify-center items-center hover:bg-blue-500/10 transition"
        >
          <UploadCloud
            className="text-blue-500 mb-6"
            size={70}
          />

          <h2 className="text-3xl font-bold text-white">
            Drag & Drop Video
          </h2>

          <p className="text-gray-400 mt-3">
            or click here to browse
          </p>

          <button
            type="button"
            className="mt-8 bg-blue-600 px-8 py-3 rounded-xl text-white font-semibold"
          >
            Choose Video
          </button>
        </div>
      )}

      {/* Video preview */}
      {screen === "preview" && video && (
        <VideoPreview
          file={video}
          onAnalyze={() => setScreen("processing")}
          onComplete={() => setScreen("completed")}
        />
      )}

      {/* Processing */}
      {screen === "processing" && (
        <ProcessingScreen
          onComplete={() => setScreen("completed")}
        />
      )}

      {/* Completed */}
      {screen === "completed" && (
        <CompletedScreen />
      )}
    </>
  );
}