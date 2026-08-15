import type { HistoryItem } from "../types";
import { getReportUrl } from "../services/api";

interface HistoryTableProps {
  items: HistoryItem[];
  onDelete: (id: number) => void;
}

export function HistoryTable({ items, onDelete }: HistoryTableProps) {
  return (
    <div className="overflow-hidden rounded-3xl border border-white/10 bg-slate-950/60 shadow-glass">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm text-slate-300">
          <thead className="bg-white/5 text-xs uppercase tracking-[0.24em] text-slate-400">
            <tr>
              <th className="px-5 py-4">File</th>
              <th className="px-5 py-4">Type</th>
              <th className="px-5 py-4">Prediction</th>
              <th className="px-5 py-4">Confidence</th>
              <th className="px-5 py-4">Date</th>
              <th className="px-5 py-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-t border-white/5">
                <td className="px-5 py-4">{item.filename}</td>
                <td className="px-5 py-4 capitalize">{item.media_type}</td>
                <td className="px-5 py-4">
                  <span className={item.prediction === "REAL" ? "text-emerald-300" : "text-rose-300"}>{item.prediction}</span>
                </td>
                <td className="px-5 py-4">{item.confidence.toFixed(1)}%</td>
                <td className="px-5 py-4">{new Date(item.created_at).toLocaleString()}</td>
                <td className="px-5 py-4">
                  <div className="flex gap-3">
                    <a className="text-cyan-300 hover:text-cyan-200" href={getReportUrl(item.id)} target="_blank" rel="noreferrer">
                      Report
                    </a>
                    <button className="text-rose-300 hover:text-rose-200" onClick={() => onDelete(item.id)}>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

