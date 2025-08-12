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


class PersonalityType(str, Enum):
    INNOVATOR = "innovator"          # 2.5% - Early adopters
    EARLY_ADOPTER = "early_adopter"  # 13.5% - Opinion leaders
    EARLY_MAJORITY = "early_majority" # 34% - Deliberate adopters
    LATE_MAJORITY = "late_majority"   # 34% - Skeptical adopters
    LAGGARD = "laggard"              # 16% - Traditional adopters


class DemographicSegment(str, Enum):
    YOUNG_LOW = "young_low"      # 18-34, low income
    YOUNG_HIGH = "young_high"    # 18-34, high income
    MIDDLE_LOW = "middle_low"    # 35-54, low income
    MIDDLE_HIGH = "middle_high"  # 35-54, high income
    SENIOR_LOW = "senior_low"    # 55+, low income
    SENIOR_HIGH = "senior_high"  # 55+, high income


class PersonalityConfig(BaseModel):
    openness: float = Field(ge=0, le=1, default=0.5, description="Openness to new experiences")
    social_influence: float = Field(ge=0, le=1, default=0.5, description="Susceptibility to social influence")
    media_affinity: float = Field(ge=0, le=1, default=0.5, description="Media consumption tendency")
    risk_tolerance: float = Field(ge=0, le=1, default=0.5, description="Risk tolerance level")


class DemographicConfig(BaseModel):
    age_group: int = Field(ge=1, le=5, default=3, description="Age group (1=18-24, 2=25-34, 3=35-44, 4=45-54, 5=55+)")
    income_level: int = Field(ge=1, le=5, default=3, description="Income level (1=very low, 5=very high)")
    urban_rural: float = Field(ge=0, le=1, default=0.5, description="Urban(1) to Rural(0) spectrum")
    education_level: int = Field(ge=1, le=5, default=3, description="Education level (1=elementary, 5=graduate)")


class InfluencerConfig(BaseModel):
    enable_influencers: bool = Field(default=True, description="Enable influencer agents")
    influencer_ratio: float = Field(ge=0, le=0.1, default=0.02, description="Percentage of influencers (0-10%)")
    influence_multiplier: float = Field(ge=1, le=10, default=3.0, description="Influence strength multiplier")
    
    
class WordOfMouthConfig(BaseModel):
    p_generate: float = Field(ge=0, le=1, default=0.08, description="Generation probability")
    decay: float = Field(ge=0, le=1, default=0.9, description="Decay factor")
    personality_weight: float = Field(ge=0, le=1, default=0.3, description="Personality influence on WoM")
    demographic_weight: float = Field(ge=0, le=1, default=0.2, description="Demographic influence on WoM")


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
    personality: PersonalityConfig = Field(default_factory=PersonalityConfig)
    demographics: DemographicConfig = Field(default_factory=DemographicConfig)
    influencers: InfluencerConfig = Field(default_factory=InfluencerConfig)
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