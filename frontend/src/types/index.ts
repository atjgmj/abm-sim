// Type definitions for the ABM simulator

export enum KPICategory {
  AWARENESS = "awareness",
  INTEREST = "interest",
  KNOWLEDGE = "knowledge", 
  LIKING = "liking",
  INTENT = "intent"
}

export enum Granularity {
  BRAND = "brand",
  SERVICE = "service",
  CAMPAIGN = "campaign"
}

export enum NetworkType {
  ERDOS_RENYI = "er",
  WATTS_STROGATZ = "ws",
  BARABASI_ALBERT = "ba"
}

export enum RunStatus {
  QUEUED = "queued",
  RUNNING = "running", 
  DONE = "done",
  ERROR = "error"
}

export interface KPIConfig {
  categories: KPICategory[];
  granularity: Granularity;
}

export interface MediaChannel {
  share: number;
  alpha: number;
}

export interface MediaMix {
  sns: MediaChannel;
  video: MediaChannel;
  search: MediaChannel;
}

export interface WordOfMouthConfig {
  p_generate: number;
  decay: number;
}

export interface NetworkConfig {
  type: NetworkType;
  n: number;
  k: number;
  beta?: number;
}

export interface ScenarioRequest {
  name: string;
  kpi: KPIConfig;
  media_mix: MediaMix;
  wom: WordOfMouthConfig;
  network: NetworkConfig;
  steps: number;
  reps: number;
  seed: number;
}

export interface ScenarioResponse {
  id: string;
  scenario: ScenarioRequest;
}

export interface RunRequest {
  scenario_id: string;
}

export interface RunResponse {
  run_id: string;
}

export interface RunStatusResponse {
  status: RunStatus;
  progress: number;
  message?: string;
}

export interface TimeSeriesPoint {
  day: number;
  metric: KPICategory;
  value: number;
}

export interface MetricSummary {
  start: number;
  end: number;
  delta: number;
}

export interface ResultsResponse {
  run_id: string;
  series: TimeSeriesPoint[];
  summary: Record<KPICategory, MetricSummary>;
}

export interface NetworkNode {
  id: number;
  label: string;
  color: string;
  size: number;
}

export interface NetworkEdge {
  from: number;
  to: number;
  width: number;
}

export interface NetworkPreviewResponse {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
}