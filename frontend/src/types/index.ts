export type Prediction = "REAL" | "DEEPFAKE";

export interface SuspiciousFrame {
  index: number;
  timestamp: number;
  confidence: number;
  note: string;
}

export interface DetectionResponse {
  prediction: Prediction;
  confidence: number;
  processing_time: number;
  faces_detected: number;
  explanation: string;
  model_name: string;
  mode: string;
  disclaimer: string;
}

export interface VideoDetectionResponse extends DetectionResponse {
  frames_analyzed: number;
  suspicious_frames: SuspiciousFrame[];
}

export interface HistoryItem {
  id: number;
  filename: string;
  media_type: "image" | "video";
  prediction: Prediction;
  confidence: number;
  processing_time: number;
  faces_detected: number;
  frames_analyzed: number;
  suspicious_frames: SuspiciousFrame[];
  explanation: string;
  model_name: string;
  mode: string;
  created_at: string;
}

export interface HistoryResponse {
  summary: {
    total_scans: number;
    image_scans: number;
    video_scans: number;
    deepfakes_detected: number;
  };
  items: HistoryItem[];
}

