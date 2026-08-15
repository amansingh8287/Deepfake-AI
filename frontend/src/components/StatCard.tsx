import { motion } from "framer-motion";

interface StatCardProps {
  label: string;
  value: string | number;
  accent: string;
}

export function StatCard({ label, value, accent }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-3xl border border-white/10 p-5 shadow-glass"
    >
      <div className="mb-3 text-sm uppercase tracking-[0.24em] text-slate-400">{label}</div>
      <div className="flex items-end justify-between gap-3">
        <div className="font-display text-4xl font-bold text-white">{value}</div>
        <div className="h-12 w-12 rounded-2xl" style={{ background: accent, boxShadow: `0 0 30px ${accent}` }} />
      </div>
    </motion.div>
  );
}

