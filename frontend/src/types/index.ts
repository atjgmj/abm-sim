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

export enum PersonalityType {
  INNOVATOR = "innovator",
  EARLY_ADOPTER = "early_adopter", 
  EARLY_MAJORITY = "early_majority",
  LATE_MAJORITY = "late_majority",
  LAGGARD = "laggard"
}

export interface PersonalityConfig {
  openness: number;
  social_influence: number;
  media_affinity: number;
  risk_tolerance: number;
}

export interface DemographicConfig {
  age_group: number;
  income_level: number;
  urban_rural: number;
  education_level: number;
}

export interface InfluencerConfig {
  enable_influencers: boolean;
  influencer_ratio: number;
  influence_multiplier: number;
}

export interface WordOfMouthConfig {
  p_generate: number;
  decay: number;
  personality_weight: number;
  demographic_weight: number;
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
  personality: PersonalityConfig;
  demographics: DemographicConfig;
  influencers: InfluencerConfig;
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