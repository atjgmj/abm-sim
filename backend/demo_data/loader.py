"""Demo data loader for external sources."""

import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class DemoDataConfig:
    """Configuration for demo data usage."""
    use_demo_data: bool = True
    data_freshness: str = "2024-01-15"  # Demo data timestamp
    disclaimer: str = "This data is for demonstration purposes only"


class DemoDataLoader:
    """Load demo data for external API simulation."""
    
    def __init__(self, demo_data_dir: Optional[str] = None):
        if demo_data_dir is None:
            # Default to demo_data directory relative to this file
            current_dir = Path(__file__).parent
            self.demo_data_dir = current_dir
        else:
            self.demo_data_dir = Path(demo_data_dir)
        
        self.config = DemoDataConfig()
    
    def load_social_media_trends(self) -> Dict[str, Any]:
        """Load social media trends demo data."""
        file_path = self.demo_data_dir / "social_media_trends.json"
        return self._load_json_file(file_path)
    
    def load_competitor_data(self, industry: str = None) -> Dict[str, Any]:
        """Load competitor analysis demo data."""
        file_path = self.demo_data_dir / "competitor_data.json"
        data = self._load_json_file(file_path)
        
        if industry and industry in data.get("industries", {}):
            # Return industry-specific data
            return {
                "industry_data": data["industries"][industry],
                "competitive_intelligence": data["competitive_intelligence"],
                "metadata": {
                    "source": "demo_data",
                    "industry": industry,
                    "last_updated": self.config.data_freshness,
                    "disclaimer": self.config.disclaimer
                }
            }
        
        return data
    
    def load_roi_benchmarks(self, industry: str = None) -> Dict[str, Any]:
        """Load ROI benchmark demo data."""
        file_path = self.demo_data_dir / "roi_benchmark.json"
        data = self._load_json_file(file_path)
        
        if industry and industry in data.get("industry_benchmarks", {}):
            # Return industry-specific benchmarks
            industry_data = data["industry_benchmarks"][industry]
            return {
                "industry": industry,
                "benchmarks": industry_data,
                "campaign_examples": [
                    campaign for campaign in data.get("campaign_performance_data", [])
                    if campaign.get("industry") == industry
                ],
                "optimization_insights": data.get("optimization_patterns", {}),
                "seasonal_trends": data.get("seasonal_trends", {}),
                "metadata": {
                    "source": "demo_data", 
                    "industry": industry,
                    "last_updated": self.config.data_freshness,
                    "disclaimer": self.config.disclaimer
                }
            }
        
        return data
    
    def load_campaign_calibration_data(self, keywords: List[str]) -> Dict[str, Any]:
        """Load campaign calibration data based on keywords."""
        # Combine relevant data from multiple sources
        trends_data = self.load_social_media_trends()
        
        # Find relevant trending topics based on keywords
        relevant_trends = []
        for trend in trends_data.get("trending_topics", []):
            if any(keyword.lower() in trend["keyword"].lower() or 
                   keyword.lower() in " ".join(trend.get("related_terms", [])).lower()
                   for keyword in keywords):
                relevant_trends.append(trend)
        
        # If no direct matches, include top trends
        if not relevant_trends:
            relevant_trends = trends_data.get("trending_topics", [])[:3]
        
        return {
            "relevant_trends": relevant_trends,
            "engagement_patterns": trends_data.get("engagement_patterns", {}),
            "demographic_insights": trends_data.get("demographic_insights", {}),
            "recommendations": self._generate_calibration_recommendations(relevant_trends),
            "metadata": {
                "source": "demo_data",
                "keywords": keywords,
                "last_updated": self.config.data_freshness,
                "disclaimer": self.config.disclaimer
            }
        }
    
    def _load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON file with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Demo data file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in demo data file {file_path}: {e}")
    
    def _generate_calibration_recommendations(self, trends: List[Dict]) -> List[str]:
        """Generate calibration recommendations based on trends."""
        recommendations = []
        
        if not trends:
            return ["No specific trends found. Consider general market approach."]
        
        avg_sentiment = sum(trend.get("sentiment", 0.5) for trend in trends) / len(trends)
        avg_growth = sum(trend.get("growth_rate", 0) for trend in trends) / len(trends)
        
        if avg_sentiment > 0.7:
            recommendations.append("高いポジティブセンチメント: エンゲージメント重視の戦略を推奨")
        elif avg_sentiment < 0.4:
            recommendations.append("ネガティブセンチメント: 慎重なアプローチと信頼構築を重視")
        
        if avg_growth > 0.2:
            recommendations.append("高成長トレンド: 積極的な予算配分を検討")
        elif avg_growth < 0:
            recommendations.append("下降トレンド: 代替戦略や新しいアプローチを検討")
        
        # Category-specific recommendations
        categories = [trend.get("category") for trend in trends]
        if "technology" in categories:
            recommendations.append("テクノロジー関連: 若年層をターゲットにしたデジタル戦略を強化")
        if "lifestyle" in categories:
            recommendations.append("ライフスタイル関連: インフルエンサーマーケティングの活用を検討")
        
        return recommendations if recommendations else ["一般的なマーケティングアプローチを推奨"]
    
    def get_data_status(self) -> Dict[str, Any]:
        """Get status of demo data availability."""
        available_files = []
        missing_files = []
        
        expected_files = [
            "social_media_trends.json",
            "competitor_data.json", 
            "roi_benchmark.json"
        ]
        
        for filename in expected_files:
            file_path = self.demo_data_dir / filename
            if file_path.exists():
                available_files.append(filename)
            else:
                missing_files.append(filename)
        
        return {
            "demo_data_enabled": self.config.use_demo_data,
            "data_directory": str(self.demo_data_dir),
            "available_files": available_files,
            "missing_files": missing_files,
            "data_freshness": self.config.data_freshness,
            "total_coverage": len(available_files) / len(expected_files),
            "status": "ready" if not missing_files else "partial"
        }


# Global instance for easy import
demo_loader = DemoDataLoader()


def get_demo_data_for_api(data_type: str, **kwargs) -> Dict[str, Any]:
    """Convenience function to get demo data for API endpoints."""
    if data_type == "social_trends":
        return demo_loader.load_social_media_trends()
    elif data_type == "competitor_analysis":
        industry = kwargs.get("industry")
        return demo_loader.load_competitor_data(industry)
    elif data_type == "roi_benchmarks":
        industry = kwargs.get("industry")
        return demo_loader.load_roi_benchmarks(industry)
    elif data_type == "campaign_calibration":
        keywords = kwargs.get("keywords", [])
        return demo_loader.load_campaign_calibration_data(keywords)
    else:
        raise ValueError(f"Unknown data type: {data_type}")