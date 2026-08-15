import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { detectImage, detectVideo } from "../services/api";
import { ResultCard } from "../components/ResultCard";
import { SuspiciousFrames } from "../components/SuspiciousFrames";
import { UploadZone } from "../components/UploadZone";
import type { DetectionResponse, VideoDetectionResponse } from "../types";

interface DetectPageProps {
  type: "image" | "video";
}

export function DetectPage({ type }: DetectPageProps) {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<DetectionResponse | VideoDetectionResponse | null>(null);

  const mutation = useMutation({
    mutationFn: async () => {
      if (!file) {
        throw new Error("Please upload a file before analysis.");
      }
      return type === "image" ? detectImage(file) : detectVideo(file);
    },
    onSuccess: (data) => setResult(data)
  });

  const accept =
    type === "image"
      ? { "image/*": [".jpg", ".jpeg", ".png", ".webp"] }
      : { "video/*": [".mp4", ".mov", ".avi", ".mkv", ".webm"] };

  function handleFileSelection(nextFile: File) {
    setFile(nextFile);
    setResult(null);
    setPreviewUrl(URL.createObjectURL(nextFile));
  }

  return (
    <div className="space-y-8">
      <section className="grid gap-6 xl:grid-cols-[1.1fr,0.9fr]">
        <div className="space-y-6">
          <div>
            <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">{type === "image" ? "Image Scan" : "Video Scan"}</p>
            <h1 className="mt-3 font-display text-4xl font-bold text-white md:text-5xl">
              {type === "image" ? "Analyze a suspicious image." : "Sample frames and score a suspicious video."}
            </h1>
          </div>
          <UploadZone
            accept={accept}
            label={type === "image" ? "Drop image or click to browse" : "Drop video or click to browse"}
            helper="Files are validated in both the browser and backend before analysis starts."
            onFileSelected={handleFileSelection}
          />
          <button
            className="rounded-full bg-cyan-300 px-6 py-3 font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
            disabled={!file || mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            {mutation.isPending ? "Analyzing..." : "Analyze"}
          </button>
          {mutation.isError ? <p className="text-sm text-rose-300">{(mutation.error as Error).message}</p> : null}
        </div>

        <div className="glass flex min-h-[320px] items-center justify-center rounded-[2rem] border border-white/10 p-4 shadow-glass">
          {previewUrl ? (
            type === "image" ? (
              <img src={previewUrl} alt="Preview" className="max-h-[420px] w-full rounded-[1.5rem] object-cover" />
            ) : (
              <video src={previewUrl} controls className="max-h-[420px] w-full rounded-[1.5rem] object-cover" />
            )
          ) : (
            <div className="text-center text-slate-400">Preview appears here after you select a file.</div>
          )}
        </div>
      </section>

      {result ? <ResultCard result={result} /> : null}
      {result && "suspicious_frames" in result ? <SuspiciousFrames items={result.suspicious_frames} /> : null}
    </div>
  );
}

