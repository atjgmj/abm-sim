"""Pydantic schemas for API requests and responses."""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class KPICategory(str, Enum):
    AWARENESS = "awareness"
    INTEREST = "interest"  
    KNOWLEDGE = "knowledge"
    LIKING = "liking"
    INTENT = "intent"


class Granularity(str, Enum):
    BRAND = "brand"
    SERVICE = "service"
    CAMPAIGN = "campaign"


class NetworkType(str, Enum):
    ERDOS_RENYI = "er"
    WATTS_STROGATZ = "ws" 
    BARABASI_ALBERT = "ba"


class RunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


class KPIConfig(BaseModel):
    categories: List[KPICategory] = Field(default=[
        KPICategory.AWARENESS,
        KPICategory.INTEREST,
        KPICategory.KNOWLEDGE,
        KPICategory.LIKING,
        KPICategory.INTENT
    ])
    granularity: Granularity = Field(default=Granularity.BRAND)


class MediaChannel(BaseModel):
    share: float = Field(ge=0, le=1, description="Budget share (0-1)")
    alpha: float = Field(ge=0, le=1, description="Effect coefficient")


class MediaMix(BaseModel):
    sns: MediaChannel = Field(default=MediaChannel(share=0.5, alpha=0.03))
    video: MediaChannel = Field(default=MediaChannel(share=0.3, alpha=0.02))
    search: MediaChannel = Field(default=MediaChannel(share=0.2, alpha=0.01))


class WordOfMouthConfig(BaseModel):
    p_generate: float = Field(ge=0, le=1, default=0.08, description="Generation probability")
    decay: float = Field(ge=0, le=1, default=0.9, description="Decay factor")


class NetworkConfig(BaseModel):
    type: NetworkType = Field(default=NetworkType.WATTS_STROGATZ)
    n: int = Field(ge=100, le=100000, default=10000, description="Number of nodes")
    k: int = Field(ge=2, le=20, default=6, description="Average degree")
    beta: Optional[float] = Field(ge=0, le=1, default=0.1, description="Rewiring probability (WS)")


class ScenarioRequest(BaseModel):
    name: str = Field(default="Baseline A")
    kpi: KPIConfig = Field(default_factory=KPIConfig)
    media_mix: MediaMix = Field(default_factory=MediaMix)
    wom: WordOfMouthConfig = Field(default_factory=WordOfMouthConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    steps: int = Field(ge=1, le=365, default=60, description="Simulation days")
    reps: int = Field(ge=1, le=100, default=10, description="Repetitions")
    seed: int = Field(default=42, description="Random seed")


class ScenarioResponse(BaseModel):
    id: str
    scenario: ScenarioRequest


class RunRequest(BaseModel):
    scenario_id: str


class RunResponse(BaseModel):
    run_id: str


class RunStatusResponse(BaseModel):
    status: RunStatus
    progress: float = Field(ge=0, le=1)
    message: Optional[str] = None


class TimeSeriesPoint(BaseModel):
    day: int
    metric: KPICategory
    value: int


class MetricSummary(BaseModel):
    start: int
    end: int
    delta: int


class ResultsResponse(BaseModel):
    run_id: str
    series: List[TimeSeriesPoint]
    summary: Dict[KPICategory, MetricSummary]


class NetworkNode(BaseModel):
    id: int
    label: str
    color: str = "#97c2fc"
    size: int = 10


class NetworkEdge(BaseModel):
    from_node: int = Field(alias="from")
    to: int
    width: float = 1.0


class NetworkPreviewResponse(BaseModel):
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]