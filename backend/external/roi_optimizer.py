"""ROI予測と予算最適化機能"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from scipy.optimize import minimize
import json
from demo_data.loader import demo_loader

@dataclass
class BudgetAllocation:
    channel: str
    current_budget: float
    optimal_budget: float
    expected_roi: float
    confidence: float

@dataclass
class ROIPrediction:
    scenario_name: str
    total_budget: float
    predicted_revenue: float
    predicted_roi: float
    confidence_interval: Tuple[float, float]
    channel_breakdown: List[BudgetAllocation]
    optimization_notes: List[str]

@dataclass
class CampaignMetrics:
    impressions: int
    clicks: int
    conversions: int
    revenue: float
    cost: float

class ROIOptimizer:
    """ROI予測と予算最適化エンジン"""
    
    def __init__(self):
        # チャネル効率性ベースライン（業界平均）- より現実的な値に調整
        self.channel_baselines = {
            'sns': {
                'cpm': 15.0,  # Cost per mille (increased for realism)
                'ctr': 0.025,  # Click-through rate (decreased)
                'cvr': 0.02,   # Conversion rate (more realistic)
                'avg_order_value': 85,  # Lower average order value
                'saturation_point': 200000  # Budget saturation
            },
            'video': {
                'cpm': 20.0,  # Higher cost for video
                'ctr': 0.035,
                'cvr': 0.025,  # More realistic conversion rate
                'avg_order_value': 120,
                'saturation_point': 150000
            },
            'search': {
                'cpm': 25.0,  # Higher cost for search ads
                'ctr': 0.045,  # Realistic CTR for search
                'cvr': 0.035,  # More realistic conversion rate
                'avg_order_value': 140,
                'saturation_point': 180000
            }
        }
    
    async def predict_roi(
        self, 
        media_mix: Dict[str, Any], 
        total_budget: float,
        historical_performance: Optional[List[Dict]] = None,
        industry: str = "technology"
    ) -> ROIPrediction:
        """ROIを予測し、予算を最適化"""
        
        try:
            # デモデータから業界ベンチマークを取得
            roi_data = demo_loader.load_roi_benchmarks(industry)
            industry_benchmarks = roi_data.get("benchmarks", {})
            
            # ベンチマークデータでチャネルベースラインを更新
            if industry_benchmarks:
                self._update_channel_baselines_from_demo(industry_benchmarks)
        except Exception as e:
            # デモデータ読み込み失敗時はデフォルトを使用
            pass
        
        # 現在の予算配分
        current_allocation = self._calculate_budget_allocation(media_mix, total_budget)
        
        # ROI予測
        predicted_metrics = self._predict_campaign_metrics(current_allocation)
        
        # 予算最適化
        optimal_allocation = self._optimize_budget_allocation(
            total_budget, 
            historical_performance,
            industry
        )
        
        # 結果の構築
        channel_breakdown = []
        total_predicted_revenue = 0
        
        for channel in ['sns', 'video', 'search']:
            current_budget = current_allocation[channel]
            optimal_budget = optimal_allocation[channel]
            
            # チャネル別ROI計算
            channel_roi = self._calculate_channel_roi(
                channel, 
                optimal_budget, 
                historical_performance
            )
            
            channel_breakdown.append(BudgetAllocation(
                channel=channel,
                current_budget=current_budget,
                optimal_budget=optimal_budget,
                expected_roi=channel_roi,
                confidence=self._calculate_confidence(channel, optimal_budget)
            ))
            
            total_predicted_revenue += optimal_budget * channel_roi
        
        overall_roi = total_predicted_revenue / total_budget if total_budget > 0 else 0
        confidence_interval = self._calculate_confidence_interval(overall_roi)
        
        optimization_notes = self._generate_optimization_notes(
            current_allocation, 
            optimal_allocation, 
            overall_roi
        )
        
        return ROIPrediction(
            scenario_name="Optimized Campaign",
            total_budget=total_budget,
            predicted_revenue=total_predicted_revenue,
            predicted_roi=overall_roi,
            confidence_interval=confidence_interval,
            channel_breakdown=channel_breakdown,
            optimization_notes=optimization_notes
        )
    
    def _calculate_budget_allocation(
        self, 
        media_mix: Dict[str, Any], 
        total_budget: float
    ) -> Dict[str, float]:
        """現在のメディアミックスから予算配分を計算"""
        allocation = {}
        
        total_share = sum(channel.get('share', 0) for channel in media_mix.values())
        
        for channel_name, channel_config in media_mix.items():
            share = channel_config.get('share', 0)
            normalized_share = share / total_share if total_share > 0 else 0
            allocation[channel_name] = total_budget * normalized_share
        
        return allocation
    
    def _predict_campaign_metrics(
        self, 
        budget_allocation: Dict[str, float]
    ) -> Dict[str, CampaignMetrics]:
        """予算配分からキャンペーン成果を予測"""
        predictions = {}
        
        for channel, budget in budget_allocation.items():
            if channel in self.channel_baselines:
                baseline = self.channel_baselines[channel]
                
                # 飽和効果を考慮した調整
                efficiency = self._calculate_efficiency_with_saturation(
                    budget, 
                    baseline['saturation_point']
                )
                
                # 基本メトリクス計算
                impressions = int(budget / baseline['cpm'] * 1000 * efficiency)
                clicks = int(impressions * baseline['ctr'])
                conversions = int(clicks * baseline['cvr'])
                revenue = conversions * baseline['avg_order_value']
                
                predictions[channel] = CampaignMetrics(
                    impressions=impressions,
                    clicks=clicks,
                    conversions=conversions,
                    revenue=revenue,
                    cost=budget
                )
        
        return predictions
    
    def _calculate_efficiency_with_saturation(
        self, 
        budget: float, 
        saturation_point: float
    ) -> float:
        """予算規模に応じた効率性を計算（飽和効果考慮）"""
        if budget <= 0:
            return 0
        
        # S字カーブで飽和効果をモデル化
        normalized_budget = budget / saturation_point
        efficiency = 2 / (1 + np.exp(-2 * normalized_budget)) - 1
        
        # 最大効率性を1.0に制限
        return min(1.0, max(0.1, efficiency))
    
    def _optimize_budget_allocation(
        self, 
        total_budget: float, 
        historical_performance: Optional[List[Dict]] = None
    ) -> Dict[str, float]:
        """予算配分を最適化"""
        
        def objective_function(allocation):
            """最大化したいROI関数"""
            sns_budget, video_budget = allocation
            search_budget = total_budget - sns_budget - video_budget
            
            if search_budget < 0:
                return -1000  # 制約違反のペナルティ
            
            allocation_dict = {
                'sns': sns_budget,
                'video': video_budget,
                'search': search_budget
            }
            
            total_roi = 0
            for channel, budget in allocation_dict.items():
                if budget > 0:
                    roi = self._calculate_channel_roi(channel, budget, historical_performance)
                    total_roi += roi * budget
            
            return -total_roi  # 最小化問題として解くため負の値を返す
        
        # 制約条件
        constraints = [
            {'type': 'ineq', 'fun': lambda x: x[0]},  # sns_budget >= 0
            {'type': 'ineq', 'fun': lambda x: x[1]},  # video_budget >= 0
            {'type': 'ineq', 'fun': lambda x: total_budget - x[0] - x[1]},  # search_budget >= 0
        ]
        
        # 境界条件
        bounds = [
            (0, total_budget),  # sns_budget bounds
            (0, total_budget),  # video_budget bounds
        ]
        
        # 初期値（均等配分）
        initial_guess = [total_budget / 3, total_budget / 3]
        
        # 最適化実行
        try:
            result = minimize(
                objective_function,
                initial_guess,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if result.success:
                sns_opt, video_opt = result.x
                search_opt = total_budget - sns_opt - video_opt
                
                return {
                    'sns': max(0, sns_opt),
                    'video': max(0, video_opt),
                    'search': max(0, search_opt)
                }
        except Exception as e:
            print(f"Optimization failed: {e}")
        
        # 最適化失敗時は均等配分
        equal_allocation = total_budget / 3
        return {
            'sns': equal_allocation,
            'video': equal_allocation,
            'search': equal_allocation
        }
    
    def _calculate_channel_roi(
        self, 
        channel: str, 
        budget: float, 
        historical_performance: Optional[List[Dict]] = None
    ) -> float:
        """チャネル別ROIを計算"""
        if budget <= 0 or channel not in self.channel_baselines:
            return 0
        
        baseline = self.channel_baselines[channel]
        
        # 効率性調整
        efficiency = self._calculate_efficiency_with_saturation(
            budget, 
            baseline['saturation_point']
        )
        
        # 基本ROI計算
        impressions = budget / baseline['cpm'] * 1000 * efficiency
        clicks = impressions * baseline['ctr']
        conversions = clicks * baseline['cvr']
        revenue = conversions * baseline['avg_order_value']
        
        roi = (revenue - budget) / budget if budget > 0 else 0
        
        # 履歴データがある場合は調整
        if historical_performance:
            historical_adjustment = self._get_historical_adjustment(
                channel, 
                historical_performance
            )
            roi *= historical_adjustment
        
        return max(0, roi)
    
    def _get_historical_adjustment(
        self, 
        channel: str, 
        historical_performance: List[Dict]
    ) -> float:
        """履歴パフォーマンスに基づく調整係数"""
        # 簡略化された実装
        # 実際の実装では過去のチャネル別パフォーマンスを分析
        return np.random.uniform(0.8, 1.2)  # プレースホルダー
    
    def _calculate_confidence(self, channel: str, budget: float) -> float:
        """予測の信頼度を計算"""
        # 予算規模と履歴データの利用可能性に基づく
        if budget <= 1000:
            return 0.6  # 少額予算は信頼度低
        elif budget <= 10000:
            return 0.8  # 中規模予算
        else:
            return 0.9  # 大規模予算は信頼度高
    
    def _calculate_confidence_interval(self, roi: float) -> Tuple[float, float]:
        """ROIの信頼区間を計算"""
        # 簡化された実装（実際にはより複雑な統計モデルを使用）
        margin = roi * 0.15  # 15%のマージン
        return (max(0, roi - margin), roi + margin)
    
    def _generate_optimization_notes(
        self, 
        current_allocation: Dict[str, float], 
        optimal_allocation: Dict[str, float], 
        predicted_roi: float
    ) -> List[str]:
        """最適化に関する注釈を生成"""
        notes = []
        
        # 配分変更の分析
        for channel in current_allocation.keys():
            current = current_allocation[channel]
            optimal = optimal_allocation[channel]
            change_pct = ((optimal - current) / current * 100) if current > 0 else 0
            
            if abs(change_pct) > 10:
                direction = "増額" if change_pct > 0 else "減額"
                notes.append(
                    f"{channel.upper()}チャネル: {abs(change_pct):.1f}%の{direction}を推奨"
                )
        
        # ROI関連の詳細分析
        if predicted_roi > 4.0:
            notes.append("優秀なROI（4.0x以上）！積極的なスケール拡大を検討してください")
        elif predicted_roi > 2.5:
            notes.append("良好なROI（2.5x以上）。現在の戦略を継続しつつ微調整を実施")
        elif predicted_roi > 1.5:
            notes.append("標準的なROI（1.5x以上）。さらなる効率改善の余地があります")
        else:
            notes.append("ROI改善が必要。高効率チャネルへの予算再配分を強く推奨")
        
        # 具体的な戦術提案
        best_channel = max(optimal_allocation.keys(), key=lambda k: optimal_allocation[k])
        notes.append(f"{best_channel.upper()}が最も投資効率の高いチャネルです")
        
        # タイミング・実施提案
        notes.append("実施タイミングは顧客の購買サイクルに合わせて調整してください")
        
        # 一般的な推奨事項
        notes.extend([
            "定期的なパフォーマンス測定と調整を実施してください",
            "A/Bテストによる継続的な最適化を推奨します",
            "季節性やイベントの影響を考慮した調整が必要です"
        ])
        
        return notes[:6]  # 上位6つの注釈を返す
    
    async def generate_ab_test_scenarios(
        self, 
        base_scenario: Dict[str, Any], 
        total_budget: float,
        test_variants: int = 3
    ) -> List[Dict[str, Any]]:
        """A/Bテストシナリオを自動生成"""
        scenarios = []
        
        # ベースシナリオ
        scenarios.append({
            "name": "Control (Current)",
            "description": "現在の設定",
            "media_mix": base_scenario.get('media_mix', {}),
            "budget": total_budget,
            "expected_lift": 0
        })
        
        # バリアント生成
        for i in range(test_variants):
            variant = self._generate_test_variant(
                base_scenario, 
                total_budget, 
                i + 1
            )
            scenarios.append(variant)
        
        return scenarios
    
    def _generate_test_variant(
        self, 
        base_scenario: Dict[str, Any], 
        total_budget: float, 
        variant_id: int
    ) -> Dict[str, Any]:
        """テストバリアントを生成"""
        base_media_mix = base_scenario.get('media_mix', {})
        
        # バリアント戦略
        strategies = [
            {
                "name": "SNS Focus",
                "description": "SNSチャネルに重点配分",
                "adjustments": {"sns_boost": 0.3, "others_reduction": 0.15}
            },
            {
                "name": "Search Heavy",
                "description": "検索広告を強化",
                "adjustments": {"search_boost": 0.4, "others_reduction": 0.2}
            },
            {
                "name": "Balanced Premium",
                "description": "全チャネル均等強化",
                "adjustments": {"all_boost": 0.2}
            }
        ]
        
        strategy = strategies[(variant_id - 1) % len(strategies)]
        
        # メディアミックス調整
        adjusted_mix = {}
        for channel, config in base_media_mix.items():
            share = config.get('share', 0)
            alpha = config.get('alpha', 0)
            
            # 戦略に基づく調整
            if strategy["name"] == "SNS Focus" and channel == "sns":
                share = min(1.0, share * 1.3)
            elif strategy["name"] == "Search Heavy" and channel == "search":
                share = min(1.0, share * 1.4)
            elif strategy["name"] == "Balanced Premium":
                share = min(1.0, share * 1.2)
            
            adjusted_mix[channel] = {
                "share": share,
                "alpha": alpha
            }
        
        # シェアの正規化
        total_share = sum(config['share'] for config in adjusted_mix.values())
        if total_share > 0:
            for channel in adjusted_mix:
                adjusted_mix[channel]['share'] /= total_share
        
        return {
            "name": f"Variant {variant_id}: {strategy['name']}",
            "description": strategy['description'],
            "media_mix": adjusted_mix,
            "budget": total_budget,
            "expected_lift": np.random.uniform(0.05, 0.25)  # 5-25%の期待上昇率
        }
    
    def _update_channel_baselines_from_demo(self, industry_benchmarks: Dict[str, Any]) -> None:
        """デモデータから取得したベンチマークでチャネルベースラインを更新"""
        channels_data = industry_benchmarks.get("channels", {})
        
        for channel_name, channel_data in channels_data.items():
            if channel_name in self.channel_baselines:
                # デモデータからCPM、CTR、CVRを更新
                self.channel_baselines[channel_name].update({
                    'cpm': channel_data.get('cpm', self.channel_baselines[channel_name]['cpm']),
                    'ctr': channel_data.get('ctr', self.channel_baselines[channel_name]['ctr']),
                    'cvr': channel_data.get('cvr', self.channel_baselines[channel_name]['cvr'])
                })