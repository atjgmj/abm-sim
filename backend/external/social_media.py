"""Social media data integration for parameter calibration."""

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import aiohttp
import numpy as np
from pydantic import BaseModel

from schemas import PersonalityConfig, DemographicConfig, MediaMix
from demo_data.loader import demo_loader

logger = logging.getLogger(__name__)


@dataclass
class SocialMediaMetrics:
    """Social media engagement metrics."""
    impressions: int
    engagement_rate: float
    reach: int
    clicks: int
    shares: int
    sentiment_score: float  # -1 to 1
    age_distribution: Dict[str, float]  # age group percentages
    device_type: Dict[str, float]  # device usage breakdown


@dataclass
class TrendingTopic:
    """Trending topic data."""
    keyword: str
    volume: int
    sentiment: float
    demographics: Dict[str, Any]
    growth_rate: float


class SocialMediaAnalyzer:
    """Analyze social media data for ABM parameter calibration."""
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_keys = api_keys or {}
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_campaign_performance(
        self, 
        campaign_keywords: List[str],
        date_range: int = 30
    ) -> Dict[str, SocialMediaMetrics]:
        """Get social media performance for campaign keywords."""
        if not self.session:
            raise RuntimeError("Analyzer not initialized. Use async context manager.")
        
        results = {}
        
        # Simulate multiple platform data collection
        for platform in ['twitter', 'instagram', 'tiktok']:
            try:
                metrics = await self._fetch_platform_data(platform, campaign_keywords, date_range)
                results[platform] = metrics
            except Exception as e:
                logger.warning(f"Failed to fetch {platform} data: {e}")
                # Provide fallback synthetic data
                results[platform] = self._generate_synthetic_metrics()
        
        return results
    
    async def _fetch_platform_data(
        self, 
        platform: str, 
        keywords: List[str], 
        date_range: int
    ) -> SocialMediaMetrics:
        """Fetch data from specific platform (mock implementation)."""
        # In real implementation, this would call actual APIs
        # For now, generate realistic synthetic data
        
        await asyncio.sleep(0.1)  # Simulate API latency
        
        base_impressions = np.random.randint(10000, 100000)
        engagement_rate = np.random.beta(2, 8)  # Typical engagement rates are low
        
        # Platform-specific adjustments
        if platform == 'twitter':
            engagement_rate *= 0.8  # Twitter tends to have lower engagement
            age_dist = {'18-24': 0.15, '25-34': 0.35, '35-44': 0.25, '45-54': 0.15, '55+': 0.10}
        elif platform == 'instagram':
            engagement_rate *= 1.5  # Instagram has higher engagement
            age_dist = {'18-24': 0.35, '25-34': 0.30, '35-44': 0.20, '45-54': 0.10, '55+': 0.05}
        else:  # tiktok
            engagement_rate *= 2.0  # TikTok has highest engagement
            age_dist = {'18-24': 0.60, '25-34': 0.25, '35-44': 0.10, '45-54': 0.03, '55+': 0.02}
        
        return SocialMediaMetrics(
            impressions=base_impressions,
            engagement_rate=min(engagement_rate, 0.15),  # Cap at 15%
            reach=int(base_impressions * np.random.uniform(0.6, 0.9)),
            clicks=int(base_impressions * engagement_rate * np.random.uniform(0.1, 0.3)),
            shares=int(base_impressions * engagement_rate * np.random.uniform(0.05, 0.15)),
            sentiment_score=np.random.normal(0.1, 0.3),  # Slightly positive bias
            age_distribution=age_dist,
            device_type={'mobile': 0.7, 'desktop': 0.25, 'tablet': 0.05}
        )
    
    def _generate_synthetic_metrics(self) -> SocialMediaMetrics:
        """Generate synthetic metrics as fallback."""
        return SocialMediaMetrics(
            impressions=np.random.randint(5000, 50000),
            engagement_rate=np.random.beta(2, 8) * 0.1,
            reach=np.random.randint(3000, 30000),
            clicks=np.random.randint(100, 1000),
            shares=np.random.randint(50, 500),
            sentiment_score=np.random.normal(0, 0.2),
            age_distribution={'18-24': 0.25, '25-34': 0.30, '35-44': 0.25, '45-54': 0.15, '55+': 0.05},
            device_type={'mobile': 0.65, 'desktop': 0.30, 'tablet': 0.05}
        )
    
    async def get_trending_topics(self, limit: int = 10) -> List[TrendingTopic]:
        """Get current trending topics from demo data."""
        try:
            # Load trending topics from demo data
            trends_data = demo_loader.load_social_media_trends()
            trending_topics = trends_data.get("trending_topics", [])
            
            topics = []
            for topic_data in trending_topics[:limit]:
                # Convert age group data from demo format
                age_groups = {}
                demo_age_data = trends_data.get("demographic_insights", {}).get("age_groups", {})
                for age_range, data in demo_age_data.items():
                    age_groups[age_range] = data.get("engagement_rate", 0.5)
                
                topics.append(TrendingTopic(
                    keyword=topic_data["keyword"],
                    volume=topic_data["volume"],
                    sentiment=topic_data["sentiment"],
                    demographics={
                        'age_groups': age_groups if age_groups else {
                            '18-24': 0.3, '25-34': 0.35, '35-44': 0.2, '45-54': 0.1, '55+': 0.05
                        }
                    },
                    growth_rate=topic_data["growth_rate"]
                ))
            
            return sorted(topics, key=lambda x: x.volume, reverse=True)
            
        except Exception as e:
            logger.warning(f"Failed to load demo trending topics: {e}")
            # Fallback to simple mock data
            return [
                TrendingTopic(
                    keyword="デモトレンド",
                    volume=50000,
                    sentiment=0.6,
                    demographics={'age_groups': {'18-24': 0.3, '25-34': 0.35, '35-44': 0.2, '45-54': 0.1, '55+': 0.05}},
                    growth_rate=0.15
                )
            ]


class ParameterCalibrator:
    """Calibrate ABM parameters using social media data."""
    
    def __init__(self):
        self.analyzer = SocialMediaAnalyzer()
    
    async def calibrate_from_campaign_data(
        self,
        campaign_keywords: List[str],
        baseline_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calibrate ABM parameters using real campaign performance data."""
        
        async with self.analyzer as analyzer:
            # Get social media performance data
            platform_data = await analyzer.get_campaign_performance(campaign_keywords)
            
            # Get trending topics for context
            trends = await analyzer.get_trending_topics()
            
        # Calibrate parameters based on data
        calibrated_params = baseline_params.copy()
        
        # Adjust media mix based on platform performance
        calibrated_params['media_mix'] = self._calibrate_media_mix(platform_data)
        
        # Adjust demographic distribution based on audience data
        calibrated_params['demographics'] = self._calibrate_demographics(platform_data)
        
        # Adjust personality parameters based on engagement patterns
        calibrated_params['personality'] = self._calibrate_personality(platform_data, trends)
        
        # Adjust WoM parameters based on sharing behavior
        calibrated_params['wom'] = self._calibrate_wom(platform_data)
        
        return calibrated_params
    
    def _calibrate_media_mix(self, platform_data: Dict[str, SocialMediaMetrics]) -> Dict[str, Any]:
        """Calibrate media mix based on platform performance."""
        total_reach = sum(metrics.reach for metrics in platform_data.values())
        
        if total_reach == 0:
            # Fallback to default distribution
            return {
                'sns': {'share': 0.5, 'alpha': 0.03},
                'video': {'share': 0.3, 'alpha': 0.02},
                'search': {'share': 0.2, 'alpha': 0.01}
            }
        
        # Map platforms to media channels
        platform_mapping = {
            'twitter': 'sns',
            'instagram': 'video',  # Instagram is visual-heavy
            'tiktok': 'video'
        }
        
        channel_performance = {'sns': 0, 'video': 0, 'search': 0.2}  # Base search allocation
        
        for platform, metrics in platform_data.items():
            channel = platform_mapping.get(platform, 'sns')
            # Weight by reach and engagement
            performance_score = metrics.reach * metrics.engagement_rate
            channel_performance[channel] += performance_score
        
        # Normalize to shares
        total_performance = sum(channel_performance.values())
        shares = {channel: perf / total_performance for channel, perf in channel_performance.items()}
        
        # Calculate alpha (effectiveness) based on engagement rates
        avg_engagement = np.mean([m.engagement_rate for m in platform_data.values()])
        base_alpha = {'sns': 0.03, 'video': 0.02, 'search': 0.01}
        
        return {
            channel: {
                'share': shares[channel],
                'alpha': base_alpha[channel] * (1 + avg_engagement * 2)  # Boost based on engagement
            }
            for channel in shares
        }
    
    def _calibrate_demographics(self, platform_data: Dict[str, SocialMediaMetrics]) -> Dict[str, Any]:
        """Calibrate demographic parameters based on audience data."""
        # Aggregate age distribution across platforms
        age_groups = ['18-24', '25-34', '35-44', '45-54', '55+']
        weighted_age_dist = {group: 0 for group in age_groups}
        total_reach = sum(m.reach for m in platform_data.values())
        
        if total_reach == 0:
            return {'age_group': 3, 'income_level': 3, 'urban_rural': 0.5, 'education_level': 3}
        
        for metrics in platform_data.values():
            weight = metrics.reach / total_reach
            for age_group, percentage in metrics.age_distribution.items():
                if age_group in weighted_age_dist:
                    weighted_age_dist[age_group] += percentage * weight
        
        # Find dominant age group
        dominant_age = max(weighted_age_dist.items(), key=lambda x: x[1])[0]
        age_mapping = {'18-24': 1, '25-34': 2, '35-44': 3, '45-54': 4, '55+': 5}
        
        return {
            'age_group': age_mapping.get(dominant_age, 3),
            'income_level': 3,  # Default to medium
            'urban_rural': 0.7,  # Social media users tend to be more urban
            'education_level': 3  # Default to college level
        }
    
    def _calibrate_personality(
        self, 
        platform_data: Dict[str, SocialMediaMetrics], 
        trends: List[TrendingTopic]
    ) -> Dict[str, float]:
        """Calibrate personality parameters based on engagement and trends."""
        avg_engagement = np.mean([m.engagement_rate for m in platform_data.values()])
        avg_sentiment = np.mean([m.sentiment_score for m in platform_data.values()])
        
        # Higher engagement suggests higher openness and social influence
        openness = 0.5 + avg_engagement * 2  # Scale engagement to openness boost
        social_influence = 0.5 + avg_engagement * 1.5
        
        # Positive sentiment suggests higher risk tolerance
        risk_tolerance = 0.5 + max(0, avg_sentiment) * 0.5
        
        # Media affinity based on platform diversity and device usage
        mobile_usage = np.mean([m.device_type.get('mobile', 0.5) for m in platform_data.values()])
        media_affinity = 0.3 + mobile_usage * 0.4  # Mobile users have higher media affinity
        
        return {
            'openness': min(1.0, openness),
            'social_influence': min(1.0, social_influence),
            'media_affinity': min(1.0, media_affinity),
            'risk_tolerance': min(1.0, risk_tolerance)
        }
    
    def _calibrate_wom(self, platform_data: Dict[str, SocialMediaMetrics]) -> Dict[str, float]:
        """Calibrate word-of-mouth parameters based on sharing behavior."""
        avg_share_rate = np.mean([
            m.shares / max(1, m.impressions) for m in platform_data.values()
        ])
        
        # Higher sharing suggests higher WoM generation
        p_generate = 0.08 + avg_share_rate * 10  # Scale to reasonable range
        
        return {
            'p_generate': min(0.2, p_generate),  # Cap at 20%
            'decay': 0.9,  # Keep default decay
            'personality_weight': 0.3,
            'demographic_weight': 0.2
        }


# API endpoint integration
class ExternalDataRequest(BaseModel):
    """Request for external data calibration."""
    campaign_keywords: List[str]
    baseline_scenario: Dict[str, Any]
    api_keys: Optional[Dict[str, str]] = None


class CalibratedParametersResponse(BaseModel):
    """Response with calibrated parameters."""
    original_params: Dict[str, Any]
    calibrated_params: Dict[str, Any]
    data_sources: List[str]
    confidence_score: float
    calibration_notes: List[str]