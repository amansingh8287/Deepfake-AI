import { useQuery } from "@tanstack/react-query";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { fetchHistory } from "../services/api";
import { StatCard } from "../components/StatCard";

export function DashboardPage() {
  const { data } = useQuery({ queryKey: ["history"], queryFn: fetchHistory });
  const summary = data?.summary;
  const chartData =
    data?.items
      .slice(0, 7)
      .reverse()
      .map((item) => ({
        name: new Date(item.created_at).toLocaleDateString(),
        confidence: Number(item.confidence.toFixed(1))
      })) ?? [];

  return (
    <div className="space-y-8">
      <section>
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Threat Intelligence</p>
        <h1 className="mt-3 max-w-3xl font-display text-4xl font-bold text-white md:text-6xl">
          Deepfake detection for images and videos, built for real final-year demos.
        </h1>
        <p className="mt-4 max-w-2xl text-lg text-slate-300">
          Analyze uploads, inspect suspicious frames, review scan history, and keep the detector honest about whether
          it is using a trained checkpoint or baseline mode.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total Scans" value={summary?.total_scans ?? 0} accent="rgba(0, 212, 255, 0.75)" />
        <StatCard label="Image Scans" value={summary?.image_scans ?? 0} accent="rgba(94, 242, 179, 0.75)" />
        <StatCard label="Video Scans" value={summary?.video_scans ?? 0} accent="rgba(255, 204, 102, 0.75)" />
        <StatCard label="Deepfakes Flagged" value={summary?.deepfakes_detected ?? 0} accent="rgba(255, 99, 125, 0.75)" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.4fr,1fr]">
        <div className="glass rounded-[2rem] border border-white/10 p-6 shadow-glass">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.24em] text-slate-400">Confidence Trend</div>
              <h2 className="mt-2 font-display text-2xl text-white">Recent scan severity</h2>
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="severity" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#00d4ff" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
                <XAxis dataKey="name" stroke="#6b7a90" />
                <YAxis stroke="#6b7a90" />
                <Tooltip />
                <Area type="monotone" dataKey="confidence" stroke="#00d4ff" fill="url(#severity)" strokeWidth={3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass rounded-[2rem] border border-white/10 p-6 shadow-glass">
          <div className="text-xs uppercase tracking-[0.24em] text-slate-400">Recent Scans</div>
          <div className="mt-4 space-y-4">
            {data?.items.slice(0, 5).map((item) => (
              <div key={item.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="font-medium text-white">{item.filename}</div>
                    <div className="mt-1 text-sm capitalize text-slate-400">{item.media_type}</div>
                  </div>
                  <div className={item.prediction === "REAL" ? "text-emerald-300" : "text-rose-300"}>{item.prediction}</div>
                </div>
              </div>
            )) ?? <p className="text-slate-400">No scans yet. Upload an image or video to begin.</p>}
          </div>
        </div>
      </section>
    </div>
  );
}

