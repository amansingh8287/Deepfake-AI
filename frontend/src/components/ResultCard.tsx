import type { DetectionResponse, VideoDetectionResponse } from "../types";

interface ResultCardProps {
  result: DetectionResponse | VideoDetectionResponse;
}

export function ResultCard({ result }: ResultCardProps) {
  const positive = result.prediction === "REAL";
  const circumference = 2 * Math.PI * 52;
  const offset = circumference - (result.confidence / 100) * circumference;

  return (
    <div className="glass rounded-3xl border border-white/10 p-6 shadow-glass">
      <div className="grid gap-6 lg:grid-cols-[auto,1fr]">
        <div className="relative mx-auto h-36 w-36">
          <svg className="h-36 w-36 -rotate-90">
            <circle cx="72" cy="72" r="52" className="fill-none stroke-white/10" strokeWidth="10" />
            <circle
              cx="72"
              cy="72"
              r="52"
              className="fill-none"
              stroke={positive ? "#5ef2b3" : "#ff637d"}
              strokeWidth="10"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className="text-3xl font-bold text-white">{result.confidence.toFixed(1)}%</div>
            <div className="text-xs uppercase tracking-[0.24em] text-slate-400">Confidence</div>
          </div>
        </div>

        <div>
          <div className="flex flex-wrap items-center gap-3">
            <span
              className={`rounded-full px-4 py-2 text-sm font-semibold ${
                positive ? "bg-emerald-400/15 text-emerald-300" : "bg-rose-400/15 text-rose-300"
              }`}
            >
              {result.prediction}
            </span>
            <span className="rounded-full bg-white/5 px-4 py-2 text-sm text-slate-300">Mode: {result.mode}</span>
            <span className="rounded-full bg-white/5 px-4 py-2 text-sm text-slate-300">{result.model_name}</span>
          </div>
          <p className="mt-4 text-sm leading-7 text-slate-300">{result.explanation}</p>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <Metric label="Processing Time" value={`${result.processing_time.toFixed(2)} s`} />
            <Metric label="Faces Detected" value={result.faces_detected} />
            {"frames_analyzed" in result ? <Metric label="Frames Analyzed" value={result.frames_analyzed} /> : null}
            {"suspicious_frames" in result ? <Metric label="Suspicious Frames" value={result.suspicious_frames.length} /> : null}
          </div>
          <p className="mt-6 rounded-2xl border border-amber-400/25 bg-amber-300/10 p-4 text-sm text-amber-100">
            {result.disclaimer}
          </p>
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <div className="text-xs uppercase tracking-[0.22em] text-slate-500">{label}</div>
      <div className="mt-2 text-xl font-semibold text-white">{value}</div>
    </div>
  );
}

