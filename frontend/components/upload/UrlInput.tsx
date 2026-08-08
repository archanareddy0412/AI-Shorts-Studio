"use client";

import { useState } from "react";

export default function UrlInput() {
  const [url, setUrl] = useState("");
  const [analyzing, setAnalyzing] = useState(false);

  async function analyzeUrl() {
    if (!url.trim()) {
      alert("Please enter a YouTube URL.");
      return;
    }

    try {
      setAnalyzing(true);

      console.log("Sending YouTube URL:", url);

      const response = await fetch(
        "http://127.0.0.1:8000/analyze-url",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            url: url,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const data = await response.json();

      console.log("Backend response:", data);

      if (!data.success) {
        throw new Error(data.error || "Analysis failed");
      }

      alert("Analysis completed!");

      console.log("Shorts:", data.result.shorts);

    } catch (error) {
      console.error("YouTube analysis error:", error);

      alert(
        error instanceof Error
          ? error.message
          : "Something went wrong."
      );
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div>
      <h2 className="text-xl font-bold text-white mb-4">
        Or Paste a YouTube URL
      </h2>

      <div className="flex gap-4">

        <input
          type="text"
          placeholder="https://youtube.com/watch?v=..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="flex-1 bg-[#0f172a] text-white rounded-xl px-5 py-4 outline-none border border-gray-700"
        />

        <button
          onClick={analyzeUrl}
          disabled={analyzing}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 px-8 rounded-xl text-white font-semibold"
        >
          {analyzing ? "Analyzing..." : "Analyze"}
        </button>

      </div>
    </div>
  );
}