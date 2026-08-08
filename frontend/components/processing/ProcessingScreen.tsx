"use client";

import { useEffect, useState } from "react";
import ProgressBar from "./ProgressBar";
import StatusItem from "./StatusItem";
import { Sparkles } from "lucide-react";

const STEPS = [
  "Uploading Video",
  "Extracting Audio",
  "Generating Transcript",
  "Finding Viral Moments",
  "Creating Shorts",
];

interface ProcessingScreenProps {
  onComplete: () => void;
}

export default function ProcessingScreen({
  onComplete,
}: ProcessingScreenProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  /*
   * The backend is doing the real work.
   *
   * We only animate the progress bar here so that
   * the screen doesn't look frozen.
   *
   * It stops at 95% and waits for VideoPreview
   * to call onComplete() when the backend finishes.
   */
  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((old) => {
        if (old >= 95) {
          return 95;
        }

        return old + 1;
      });
    }, 500);

    return () => clearInterval(timer);
  }, []);

  /*
   * Change the displayed processing step
   * based on the progress.
   */
  useEffect(() => {
    const step = Math.min(
      Math.floor(progress / 20),
      STEPS.length - 1
    );

    setCurrentStep(step);
  }, [progress]);

  return (
    <div className="bg-[#111827] border border-blue-500/30 rounded-3xl p-8">

      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <Sparkles className="text-blue-500" />

        <h2 className="text-3xl font-bold text-white">
          AI Processing
        </h2>
      </div>

      {/* Progress */}
      <ProgressBar progress={progress} />

      {/* Processing steps */}
      <div className="space-y-4 mt-10">
        {STEPS.map((step, index) => (
          <StatusItem
            key={step}
            title={step}
            active={
              index === currentStep &&
              progress < 95
            }
            completed={index < currentStep}
          />
        ))}
      </div>

      {/* Message */}
      <p className="text-center text-gray-400 mt-10">
        Please wait while AI analyzes your video...
      </p>

    </div>
  );
}