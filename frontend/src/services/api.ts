import axios from "axios";
import type { DetectionResponse, HistoryResponse, VideoDetectionResponse } from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api"
});

export async function fetchHistory(): Promise<HistoryResponse> {
  const { data } = await api.get<HistoryResponse>("/history");
  return data;
}

export async function detectImage(file: File): Promise<DetectionResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<DetectionResponse>("/detect/image", formData);
  return data;
}

export async function detectVideo(file: File): Promise<VideoDetectionResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<VideoDetectionResponse>("/detect/video", formData);
  return data;
}

export async function deleteHistoryItem(id: number): Promise<void> {
  await api.delete(`/history/${id}`);
}

export function getReportUrl(id: number): string {
  return `${api.defaults.baseURL}/report/${id}`;
}

