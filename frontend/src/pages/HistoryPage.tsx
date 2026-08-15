import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { deleteHistoryItem, fetchHistory } from "../services/api";
import { HistoryTable } from "../components/HistoryTable";

export function HistoryPage() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["history"], queryFn: fetchHistory });
  const deleteMutation = useMutation({
    mutationFn: deleteHistoryItem,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["history"] })
  });

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Audit Trail</p>
        <h1 className="mt-3 font-display text-4xl font-bold text-white">Detection history and downloadable reports</h1>
      </div>
      {isLoading ? (
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-slate-300">Loading history...</div>
      ) : (
        <HistoryTable items={data?.items ?? []} onDelete={(id) => deleteMutation.mutate(id)} />
      )}
    </div>
  );
}

