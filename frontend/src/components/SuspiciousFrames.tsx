import type { SuspiciousFrame } from "../types";

export function SuspiciousFrames({ items }: { items: SuspiciousFrame[] }) {
  if (!items.length) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/5 p-5 text-sm text-slate-400">
        No sampled frames crossed the suspicious threshold.
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {items.map((frame) => (
        <div key={`${frame.index}-${frame.timestamp}`} className="glass rounded-3xl border border-white/10 p-5">
          <div className="font-display text-xl text-white">Frame {frame.index}</div>
          <div className="mt-2 text-sm text-slate-400">{frame.timestamp.toFixed(2)} seconds</div>
          <div className="mt-3 text-lg font-semibold text-rose-300">{frame.confidence.toFixed(1)}%</div>
          <p className="mt-3 text-sm text-slate-300">{frame.note}</p>
        </div>
      ))}
    </div>
  );
}

