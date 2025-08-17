"""競合分析とベンチマーキング機能"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
from demo_data.loader import demo_loader

class IndustryType(str, Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    RETAIL = "retail"
    EDUCATION = "education"
    AUTOMOTIVE = "automotive"
    FOOD_BEVERAGE = "food_beverage"
    FASHION = "fashion"

@dataclass
class CompetitorMetric:
    company: str
    awareness_rate: float
    market_share: float
    social_engagement: float
    media_spend: float
    conversion_rate: float

@dataclass
class IndustryBenchmark:
    industry: IndustryType
    avg_awareness_rate: float
    avg_conversion_rate: float
    avg_social_engagement: float
    avg_media_efficiency: float
    top_quartile_thresholds: Dict[str, float]

@dataclass
class CompetitorAnalysis:
    target_company: str
    industry: IndustryType
    competitors: List[CompetitorMetric]
    market_position: str  # "leader", "challenger", "follower", "niche"
    strengths: List[str]
    opportunities: List[str]
    threats: List[str]
    recommended_strategies: List[str]

class CompetitorAnalyzer:
    """競合分析とベンチマーキング"""
    
    def __init__(self):
        # 業界ベンチマークデータ（実際の実装では外部データソースから取得）
        self.industry_benchmarks = {
            IndustryType.TECHNOLOGY: IndustryBenchmark(
                industry=IndustryType.TECHNOLOGY,
                avg_awareness_rate=0.35,
                avg_conversion_rate=0.08,
                avg_social_engagement=0.045,
                avg_media_efficiency=0.12,
                top_quartile_thresholds={
                    "awareness": 0.55,
                    "conversion": 0.15,
                    "engagement": 0.08,
                    "efficiency": 0.20
                }
            ),
            IndustryType.RETAIL: IndustryBenchmark(
                industry=IndustryType.RETAIL,
                avg_awareness_rate=0.42,
                avg_conversion_rate=0.12,
                avg_social_engagement=0.06,
                avg_media_efficiency=0.15,
                top_quartile_thresholds={
                    "awareness": 0.65,
                    "conversion": 0.22,
                    "engagement": 0.12,
                    "efficiency": 0.25
                }
            ),
            IndustryType.FINANCE: IndustryBenchmark(
                industry=IndustryType.FINANCE,
                avg_awareness_rate=0.28,
                avg_conversion_rate=0.05,
                avg_social_engagement=0.025,
                avg_media_efficiency=0.08,
                top_quartile_thresholds={
                    "awareness": 0.45,
                    "conversion": 0.10,
                    "engagement": 0.05,
                    "efficiency": 0.15
                }
            )
        }
    
    async def analyze_competitors(
        self, 
        industry: IndustryType, 
        keywords: List[str]
    ) -> CompetitorAnalysis:
        """競合分析を実行"""
        
        try:
            # デモデータから競合情報を取得
            competitor_data = demo_loader.load_competitor_data(industry.value)
            industry_data = competitor_data.get("industry_data", {})
            
            # デモデータから競合他社情報を構築
            competitors = []
            market_leaders = industry_data.get("market_leaders", [])
            
            for leader in market_leaders:
                competitors.append(CompetitorMetric(
                    company=leader["company"],
                    awareness_rate=leader["awareness_rate"],
                    market_share=leader["market_share"],
                    social_engagement=leader["social_engagement"],
                    media_spend=leader["media_spend"],
                    conversion_rate=leader["conversion_rate"]
                ))
            
            # 市場ポジション分析
            market_position = self._analyze_market_position_from_demo(industry_data)
            
            # SWOT分析（デモデータベース）
            strengths, opportunities, threats = self._perform_swot_analysis_from_demo(
                industry_data, competitor_data.get("competitive_intelligence", {})
            )
            
            # 戦略提案
            strategies = self._generate_strategies_from_demo(industry_data, keywords)
            
            return CompetitorAnalysis(
                target_company="Your Company",
                industry=industry,
                competitors=competitors,
                market_position=market_position,
                strengths=strengths,
                opportunities=opportunities,
                threats=threats,
                recommended_strategies=strategies
            )
            
        except Exception as e:
            print(f"Debug: Error in analyze_competitors: {e}")
            import traceback
            traceback.print_exc()
            # フォールバック: 従来のシンプルな生成方式
            competitors = self._generate_synthetic_competitors(industry)
            market_position = self._analyze_market_position(competitors)
            strengths, opportunities, threats = self._perform_swot_analysis(industry, competitors)
            strategies = self._generate_strategies(industry, market_position, opportunities)
            
            return CompetitorAnalysis(
                target_company="Your Company",
                industry=industry,
                competitors=competitors,
                market_position=market_position,
                strengths=strengths,
                opportunities=opportunities,
                threats=threats,
                recommended_strategies=strategies
            )
    
    def _generate_synthetic_competitors(self, industry: IndustryType) -> List[CompetitorMetric]:
        """業界に応じた合成競合データを生成"""
        benchmark = self.industry_benchmarks.get(industry)
        if not benchmark:
            benchmark = self.industry_benchmarks[IndustryType.TECHNOLOGY]
        
        competitors = []
        # 業界別に異なる競合企業名を生成
        company_templates = {
            IndustryType.TECHNOLOGY: [
                "TechGiant Solutions", "CloudInnovate Corp", "DataDriven Inc", 
                "NextGen Systems", "AI Pioneer Ltd"
            ],
            IndustryType.RETAIL: [
                "MegaMart Chain", "Fashion Forward Co", "Digital Commerce Inc",
                "Customer First Retail", "Trendy Lifestyle Ltd"
            ],
            IndustryType.FINANCE: [
                "Global Finance Group", "Digital Banking Corp", "Investment Pro Inc",
                "FinTech Innovators", "Secure Capital Ltd"
            ],
            IndustryType.HEALTHCARE: [
                "HealthCare Prime", "MedTech Solutions", "Wellness First Corp",
                "Digital Health Inc", "Care Innovation Ltd"
            ],
            IndustryType.EDUCATION: [
                "EduTech Leaders", "Learning Solutions Corp", "Knowledge Hub Inc",
                "Future Education Co", "Smart Learning Ltd"
            ],
            IndustryType.AUTOMOTIVE: [
                "AutoTech Corp", "Mobility Solutions Inc", "Smart Cars Co",
                "Electric Future Ltd", "DriveInnovation Group"
            ]
        }
        
        company_names = company_templates.get(industry, company_templates[IndustryType.TECHNOLOGY])
        
        for i, name in enumerate(company_names):
            # 業界平均を基準にバリエーションを生成
            base_multiplier = 1.2 - (i * 0.1)  # Leader to follower gradient
            
            competitors.append(CompetitorMetric(
                company=name,
                awareness_rate=min(1.0, benchmark.avg_awareness_rate * base_multiplier * np.random.uniform(0.8, 1.2)),
                market_share=np.random.uniform(0.05, 0.35) if i == 0 else np.random.uniform(0.02, 0.15),
                social_engagement=min(1.0, benchmark.avg_social_engagement * base_multiplier * np.random.uniform(0.7, 1.3)),
                media_spend=np.random.uniform(50000, 500000) * base_multiplier,
                conversion_rate=min(1.0, benchmark.avg_conversion_rate * base_multiplier * np.random.uniform(0.6, 1.4))
            ))
        
        return competitors
    
    def _analyze_market_position(self, competitors: List[CompetitorMetric]) -> str:
        """市場ポジションを分析"""
        # 自社を平均的な位置と仮定
        avg_awareness = np.mean([c.awareness_rate for c in competitors])
        avg_market_share = np.mean([c.market_share for c in competitors])
        
        # 簡単なポジショニング
        if avg_awareness > 0.4 and avg_market_share > 0.15:
            return "leader"
        elif avg_awareness > 0.3 and avg_market_share > 0.08:
            return "challenger"
        elif avg_awareness > 0.2:
            return "follower"
        else:
            return "niche"
    
    def _perform_swot_analysis(
        self, 
        industry: IndustryType, 
        competitors: List[CompetitorMetric]
    ) -> tuple[List[str], List[str], List[str]]:
        """SWOT分析を実行"""
        
        strengths = [
            "Advanced analytics and data-driven approach",
            "Agile campaign optimization capabilities",
            "Strong digital presence foundation"
        ]
        
        opportunities = [
            "Growing market demand in target segments",
            "Emerging social media platforms adoption",
            "Increasing focus on personalized marketing"
        ]
        
        threats = [
            "Intense competition from established players",
            "Rising customer acquisition costs",
            "Regulatory changes in digital advertising"
        ]
        
        # 業界固有の調整
        if industry == IndustryType.TECHNOLOGY:
            opportunities.append("AI and machine learning adoption trends")
            threats.append("Rapid technology change and innovation cycles")
        elif industry == IndustryType.FINANCE:
            opportunities.append("Digital transformation in financial services")
            threats.append("Strict regulatory compliance requirements")
        
        return strengths, opportunities, threats
    
    def _generate_strategies(
        self, 
        industry: IndustryType, 
        position: str, 
        opportunities: List[str]
    ) -> List[str]:
        """戦略的提案を生成"""
        
        base_strategies = [
            "Implement multi-channel attribution modeling",
            "Enhance customer journey personalization",
            "Optimize media mix allocation based on real-time performance"
        ]
        
        # ポジション別戦略
        if position == "leader":
            base_strategies.extend([
                "Defend market position through innovation",
                "Expand into adjacent market segments",
                "Build strategic partnerships for ecosystem growth"
            ])
        elif position == "challenger":
            base_strategies.extend([
                "Focus on differentiation and unique value proposition",
                "Target competitors' weak spots",
                "Invest in emerging channels and technologies"
            ])
        else:
            base_strategies.extend([
                "Find and dominate niche segments",
                "Build cost-effective acquisition channels",
                "Focus on customer retention and loyalty"
            ])
        
        return base_strategies[:6]  # Return top 6 strategies

    async def get_industry_insights(self, industry: IndustryType) -> Dict[str, Any]:
        """業界インサイトを取得"""
        benchmark = self.industry_benchmarks.get(industry)
        if not benchmark:
            benchmark = self.industry_benchmarks[IndustryType.TECHNOLOGY]
        
        return {
            "industry_overview": {
                "average_awareness_rate": benchmark.avg_awareness_rate,
                "average_conversion_rate": benchmark.avg_conversion_rate,
                "average_engagement_rate": benchmark.avg_social_engagement,
                "media_efficiency_benchmark": benchmark.avg_media_efficiency
            },
            "performance_thresholds": benchmark.top_quartile_thresholds,
            "market_trends": self._get_market_trends(industry),
            "success_factors": self._get_success_factors(industry)
        }
    
    def _get_market_trends(self, industry: IndustryType) -> List[str]:
        """業界トレンドを取得"""
        trends_map = {
            IndustryType.TECHNOLOGY: [
                "AI-powered personalization is becoming standard",
                "Voice search optimization gaining importance",
                "Privacy-first marketing strategies emerging"
            ],
            IndustryType.RETAIL: [
                "Omnichannel experiences driving engagement",
                "Social commerce integration accelerating",
                "Sustainability messaging resonating with consumers"
            ],
            IndustryType.FINANCE: [
                "Digital-first customer experiences expected",
                "Trust and security messaging critical",
                "Educational content driving conversions"
            ]
        }
        return trends_map.get(industry, trends_map[IndustryType.TECHNOLOGY])
    
    def _get_success_factors(self, industry: IndustryType) -> List[str]:
        """成功要因を取得"""
        factors_map = {
            IndustryType.TECHNOLOGY: [
                "Innovation leadership and thought leadership content",
                "Technical credibility and proof of concept demonstrations",
                "Developer community engagement"
            ],
            IndustryType.RETAIL: [
                "Visual storytelling and product demonstration",
                "User-generated content and social proof",
                "Seasonal campaign optimization"
            ],
            IndustryType.FINANCE: [
                "Educational content and financial literacy",
                "Trust signals and regulatory compliance",
                "Personalized financial advice and tools"
            ]
        }
        return factors_map.get(industry, factors_map[IndustryType.TECHNOLOGY])
    
    def _analyze_market_position_from_demo(self, industry_data: Dict[str, Any]) -> str:
        """デモデータから市場ポジションを分析"""
        market_trends = industry_data.get("market_trends", {})
        growth_rate = market_trends.get("growth_rate", 0.1)
        
        if growth_rate > 0.12:
            return "成長市場での新規参入機会"
        elif growth_rate > 0.08:
            return "安定成長市場でのポジション確立"
        else:
            return "成熟市場での差別化戦略"
    
    def _perform_swot_analysis_from_demo(self, industry_data: Dict, competitive_intel: Dict) -> tuple:
        """デモデータからSWOT分析を実行"""
        market_trends = industry_data.get("market_trends", {})
        key_trends = market_trends.get("key_trends", [])
        customer_priorities = market_trends.get("customer_priorities", [])
        
        # 強み（業界トレンドに基づく）
        strengths = [
            f"{trend}への対応力" for trend in key_trends[:2]
        ] + ["データドリブンなアプローチ", "革新的な技術活用"]
        
        # 機会（顧客ニーズと市場動向から）
        opportunities = [
            f"{priority}の向上ニーズへの対応" for priority in customer_priorities[:2]
        ] + [f"{trend}市場の拡大" for trend in key_trends[:1]]
        
        # 脅威（競争環境から）
        threats = [
            "既存企業の市場支配力",
            "価格競争の激化",
            "技術変化のスピード",
            "顧客期待値の上昇"
        ]
        
        return strengths[:4], opportunities[:4], threats[:4]
    
    def _generate_strategies_from_demo(self, industry_data: Dict, keywords: List[str]) -> List[str]:
        """デモデータとキーワードから戦略を生成"""
        market_trends = industry_data.get("market_trends", {})
        key_trends = market_trends.get("key_trends", [])
        customer_priorities = market_trends.get("customer_priorities", [])
        
        strategies = []
        
        # トレンドベース戦略
        if key_trends:
            strategies.append(f"{key_trends[0]}を活用した差別化戦略")
        
        # 顧客重視戦略
        if customer_priorities:
            strategies.append(f"{customer_priorities[0]}に特化したサービス開発")
        
        # キーワードベース戦略
        if keywords:
            strategies.append(f"{', '.join(keywords[:2])}を軸としたブランディング強化")
        
        # 一般的戦略
        strategies.extend([
            "デジタルマーケティングの最適化",
            "顧客体験の向上とロイヤリティ構築",
            "データ分析による継続的な改善"
        ])
        
        return strategies[:6]