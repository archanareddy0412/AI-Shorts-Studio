"use client";

import { useRef } from "react";
import { useRouter } from "next/navigation";

export default function Hero() {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const router = useRouter();

  function uploadVideo() {
    inputRef.current?.click();
  }

  function pasteYouTubeURL() {
    router.push("/dashboard");
  }

  function handleFileChange(
    e: React.ChangeEvent<HTMLInputElement>
  ) {
    const file = e.target.files?.[0];

    if (!file) {
      return;
    }

    console.log("Selected video:", file.name);

    // Go to dashboard.
    // The dashboard will handle the actual upload/processing.
    router.push("/dashboard");
  }

  return (
    <section className="relative min-h-screen overflow-hidden bg-black">

      {/* Background glow */}
      <div className="absolute h-[600px] w-[600px] rounded-full bg-blue-600/20 blur-[150px]" />

      <div className="absolute right-20 top-40 h-[350px] w-[350px] rounded-full bg-purple-600/20 blur-[120px]" />

      {/* Hidden video input */}
      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        onChange={handleFileChange}
        className="hidden"
      />

      <div className="relative z-10 mx-auto max-w-5xl px-6 pt-32 text-center">

        <p className="mb-6 text-blue-400 font-semibold tracking-widest uppercase">
          AI Powered Video Clipping
        </p>

        <h1 className="text-7xl font-black leading-tight text-white">

          Turn Long Videos

          <br />

          Into

          <span className="text-blue-500">
            {" "}Viral Shorts
          </span>

        </h1>

        <p className="mx-auto mt-8 max-w-3xl text-xl text-gray-400">

          Upload your videos or paste YouTube links.

          AI automatically finds viral moments,

          adds captions and exports ready-to-share Shorts.

        </p>

        <div className="mt-12 flex flex-wrap justify-center gap-5">

          {/* Upload Video */}
          <button
            type="button"
            onClick={uploadVideo}
            className="rounded-xl bg-blue-600 px-8 py-4 text-lg font-semibold text-white hover:bg-blue-700 transition"
          >
            Upload Video
          </button>

          {/* YouTube URL */}
          <button
            type="button"
            onClick={pasteYouTubeURL}
            className="rounded-xl border border-gray-700 px-8 py-4 text-lg text-white hover:bg-gray-900 transition"
          >
            Paste YouTube URL
          </button>

        </div>

      </div>

    </section>
  );
}