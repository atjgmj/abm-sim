import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  DollarSign, 
  Target, 
  BarChart3, 
  Lightbulb,
  Users,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Calculator,
  PieChart
} from 'lucide-react';
import { ScenarioRequest } from '../types';
import { Tooltip } from './Tooltip';
import { PARAMETER_TOOLTIPS } from '../utils/tooltips';

interface Props {
  scenario: ScenarioRequest;
  onCalibratedScenario: (calibrated: ScenarioRequest) => void;
}

interface CompetitorData {
  company: string;
  awareness_rate: number;
  market_share: number;
  social_engagement: number;
  media_spend: number;
  conversion_rate: number;
}

interface CompetitorAnalysis {
  target_company: string;
  industry: string;
  market_position: string;
  competitors: CompetitorData[];
  strengths: string[];
  opportunities: string[];
  threats: string[];
  recommended_strategies: string[];
}

interface ROIPrediction {
  scenario_name: string;
  total_budget: number;
  predicted_revenue: number;
  predicted_roi: number;
  confidence_interval: [number, number];
  channel_breakdown: {
    channel: string;
    current_budget: number;
    optimal_budget: number;
    expected_roi: number;
    confidence: number;
  }[];
  optimization_notes: string[];
}

interface ABTestScenario {
  name: string;
  description: string;
  media_mix: any;
  budget: number;
  expected_lift: number;
}

export const AdvancedCalibration: React.FC<Props> = ({ scenario, onCalibratedScenario }) => {
  const [activeTab, setActiveTab] = useState<'competitor' | 'roi' | 'abtest' | 'mlopt'>('competitor');
  const [isLoading, setIsLoading] = useState(false);
  
  // Competitor Analysis State
  const [industry, setIndustry] = useState('technology');
  const [competitorAnalysis, setCompetitorAnalysis] = useState<CompetitorAnalysis | null>(null);
  
  // ROI Prediction State
  const [totalBudget, setTotalBudget] = useState(100000);
  const [roiPrediction, setROIPrediction] = useState<ROIPrediction | null>(null);
  
  // A/B Testing State
  const [abTestScenarios, setABTestScenarios] = useState<ABTestScenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<string>('');

  const industries = [
    { value: 'technology', label: 'テクノロジー' },
    { value: 'retail', label: '小売' },
    { value: 'finance', label: '金融' },
    { value: 'healthcare', label: 'ヘルスケア' },
    { value: 'education', label: '教育' },
    { value: 'automotive', label: '自動車' }
  ];

  const handleCompetitorAnalysis = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/competitor-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          industry,
          keywords: ['marketing', 'campaign']
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setCompetitorAnalysis(data.analysis);
      }
    } catch (error) {
      console.error('Competitor analysis failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleROIPrediction = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/roi-prediction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          media_mix: scenario.media_mix,
          total_budget: totalBudget
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setROIPrediction(data.roi_prediction);
      }
    } catch (error) {
      console.error('ROI prediction failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleABTestGeneration = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/ab-test-scenarios', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          base_scenario: scenario,
          total_budget: totalBudget,
          test_variants: 3
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setABTestScenarios(data.test_scenarios);
      }
    } catch (error) {
      console.error('A/B test generation failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const applyOptimizedScenario = () => {
    if (roiPrediction) {
      // ROI最適化結果を現在のシナリオに適用
      const optimizedScenario = { ...scenario };
      
      roiPrediction.channel_breakdown.forEach(channel => {
        const totalOptimalBudget = roiPrediction.channel_breakdown.reduce(
          (sum, ch) => sum + ch.optimal_budget, 0
        );
        
        if (totalOptimalBudget > 0) {
          const share = channel.optimal_budget / totalOptimalBudget;
          if (optimizedScenario.media_mix[channel.channel as keyof typeof optimizedScenario.media_mix]) {
            optimizedScenario.media_mix[channel.channel as keyof typeof optimizedScenario.media_mix].share = share;
          }
        }
      });
      
      onCalibratedScenario(optimizedScenario);
    }
  };

  const getMarketPositionColor = (position: string) => {
    switch (position) {
      case 'leader': return 'text-green-600 bg-green-100';
      case 'challenger': return 'text-blue-600 bg-blue-100';
      case 'follower': return 'text-yellow-600 bg-yellow-100';
      case 'niche': return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
      minimumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <BarChart3 className="h-6 w-6 text-blue-600" />
          <h3 className="text-xl font-bold text-gray-900">Advanced Campaign Intelligence</h3>
          <span className="px-2 py-1 bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700 text-xs rounded-full font-medium">
            PREMIUM
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'competitor', label: '競合分析', icon: Users },
            { id: 'roi', label: 'ROI最適化', icon: DollarSign },
            { id: 'abtest', label: 'A/Bテスト設計', icon: Target },
          ].map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Competitor Analysis Tab */}
      {activeTab === 'competitor' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg border">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-medium text-gray-900">競合・市場分析</h4>
              <Tooltip content="業界データに基づく競合ポジション分析" position="left" />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">業界</label>
                <select
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {industries.map(ind => (
                    <option key={ind.value} value={ind.value}>{ind.label}</option>
                  ))}
                </select>
              </div>
              
              <div className="flex items-end">
                <button
                  onClick={handleCompetitorAnalysis}
                  disabled={isLoading}
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {isLoading ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : <Users className="h-4 w-4 mr-2" />}
                  分析実行
                </button>
              </div>
            </div>

            {competitorAnalysis && (
              <div className="space-y-6">
                {/* Market Position */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h5 className="font-medium text-gray-900 mb-2">市場ポジション</h5>
                  <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getMarketPositionColor(competitorAnalysis.market_position)}`}>
                    {competitorAnalysis.market_position.toUpperCase()}
                  </span>
                  <p className="text-sm text-gray-600 mt-2">
                    {competitorAnalysis.industry}業界における現在の市場での立ち位置
                  </p>
                </div>

                {/* Competitor Comparison */}
                <div>
                  <h5 className="font-medium text-gray-900 mb-3">競合比較</h5>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">企業</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">認知率</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">市場シェア</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SNS関与率</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">コンバージョン率</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {competitorAnalysis.competitors.map((comp, idx) => (
                          <tr key={idx}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {comp.company}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {(comp.awareness_rate * 100).toFixed(1)}%
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {(comp.market_share * 100).toFixed(1)}%
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {(comp.social_engagement * 100).toFixed(1)}%
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {(comp.conversion_rate * 100).toFixed(1)}%
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Strategic Recommendations */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h5 className="flex items-center font-medium text-gray-900 mb-3">
                      <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                      機会
                    </h5>
                    <ul className="space-y-2">
                      {competitorAnalysis.opportunities.map((opp, idx) => (
                        <li key={idx} className="text-sm text-gray-600 flex items-start">
                          <span className="text-green-600 mr-2">•</span>
                          {opp}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h5 className="flex items-center font-medium text-gray-900 mb-3">
                      <Lightbulb className="h-5 w-5 text-yellow-600 mr-2" />
                      推奨戦略
                    </h5>
                    <ul className="space-y-2">
                      {competitorAnalysis.recommended_strategies.slice(0, 4).map((strategy, idx) => (
                        <li key={idx} className="text-sm text-gray-600 flex items-start">
                          <span className="text-blue-600 mr-2">•</span>
                          {strategy}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ROI Optimization Tab */}
      {activeTab === 'roi' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg border">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-medium text-gray-900">ROI予測＆予算最適化</h4>
              <Tooltip content="機械学習によるROI予測と予算配分最適化" position="left" />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">総予算（円）</label>
                <input
                  type="number"
                  value={totalBudget}
                  onChange={(e) => setTotalBudget(parseInt(e.target.value))}
                  min="10000"
                  max="10000000"
                  step="10000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-end">
                <button
                  onClick={handleROIPrediction}
                  disabled={isLoading}
                  className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
                >
                  {isLoading ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : <Calculator className="h-4 w-4 mr-2" />}
                  ROI予測
                </button>
              </div>
            </div>

            {roiPrediction && (
              <div className="space-y-6">
                {/* ROI Summary */}
                <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {roiPrediction.predicted_roi.toFixed(2)}x
                      </div>
                      <div className="text-sm text-gray-600">予測ROI</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {formatCurrency(roiPrediction.predicted_revenue)}
                      </div>
                      <div className="text-sm text-gray-600">予測収益</div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-600">信頼区間</div>
                      <div className="text-lg font-medium text-gray-800">
                        {roiPrediction.confidence_interval[0].toFixed(2)}x - {roiPrediction.confidence_interval[1].toFixed(2)}x
                      </div>
                    </div>
                  </div>
                </div>

                {/* Channel Optimization */}
                <div>
                  <h5 className="font-medium text-gray-900 mb-3">チャネル別最適化</h5>
                  <div className="space-y-4">
                    {roiPrediction.channel_breakdown.map(channel => (
                      <div key={channel.channel} className="bg-gray-50 p-4 rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <h6 className="font-medium text-gray-900 capitalize">
                            {channel.channel.toUpperCase()}
                          </h6>
                          <span className="text-sm text-gray-600">
                            信頼度: {(channel.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500">現在予算:</span>
                            <div className="font-medium">{formatCurrency(channel.current_budget)}</div>
                          </div>
                          <div>
                            <span className="text-gray-500">最適予算:</span>
                            <div className="font-medium text-blue-600">
                              {formatCurrency(channel.optimal_budget)}
                            </div>
                          </div>
                          <div>
                            <span className="text-gray-500">期待ROI:</span>
                            <div className="font-medium text-green-600">
                              {channel.expected_roi.toFixed(2)}x
                            </div>
                          </div>
                        </div>
                        
                        {/* Budget Change Indicator */}
                        <div className="mt-2">
                          {channel.optimal_budget > channel.current_budget ? (
                            <span className="inline-flex items-center text-xs text-green-600">
                              <TrendingUp className="h-3 w-3 mr-1" />
                              +{formatCurrency(channel.optimal_budget - channel.current_budget)} 推奨
                            </span>
                          ) : channel.optimal_budget < channel.current_budget ? (
                            <span className="inline-flex items-center text-xs text-red-600">
                              <TrendingUp className="h-3 w-3 mr-1 rotate-180" />
                              {formatCurrency(channel.optimal_budget - channel.current_budget)} 推奨
                            </span>
                          ) : (
                            <span className="text-xs text-gray-500">適切な配分です</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Optimization Notes */}
                <div>
                  <h5 className="font-medium text-gray-900 mb-3">最適化提案</h5>
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <ul className="space-y-2">
                      {roiPrediction.optimization_notes.map((note, idx) => (
                        <li key={idx} className="text-sm text-blue-800 flex items-start">
                          <Lightbulb className="h-4 w-4 text-blue-600 mr-2 flex-shrink-0 mt-0.5" />
                          {note}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Apply Optimization Button */}
                <div className="flex justify-end">
                  <button
                    onClick={applyOptimizedScenario}
                    className="flex items-center px-6 py-3 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-md hover:from-green-700 hover:to-blue-700 font-medium"
                  >
                    <CheckCircle className="h-5 w-5 mr-2" />
                    最適化を適用
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* A/B Test Tab */}
      {activeTab === 'abtest' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg border">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-medium text-gray-900">A/Bテスト設計</h4>
              <Tooltip content="統計的に有意なA/Bテストシナリオを自動生成" position="left" />
            </div>
            
            <div className="flex justify-between items-center mb-4">
              <p className="text-sm text-gray-600">
                現在のシナリオを基準に、最適化されたテストパターンを生成します
              </p>
              
              <button
                onClick={handleABTestGeneration}
                disabled={isLoading}
                className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
              >
                {isLoading ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : <Target className="h-4 w-4 mr-2" />}
                テスト生成
              </button>
            </div>

            {abTestScenarios.length > 0 && (
              <div className="space-y-4">
                <h5 className="font-medium text-gray-900">推奨テストシナリオ</h5>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {abTestScenarios.map((testScenario, idx) => (
                    <div 
                      key={idx} 
                      className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                        selectedScenario === testScenario.name 
                          ? 'border-purple-500 bg-purple-50' 
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setSelectedScenario(testScenario.name)}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h6 className="font-medium text-gray-900">{testScenario.name}</h6>
                        {testScenario.expected_lift > 0 && (
                          <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                            +{(testScenario.expected_lift * 100).toFixed(0)}%
                          </span>
                        )}
                      </div>
                      
                      <p className="text-sm text-gray-600 mb-3">{testScenario.description}</p>
                      
                      <div className="text-xs text-gray-500 space-y-1">
                        <div>予算: {formatCurrency(testScenario.budget)}</div>
                        {testScenario.media_mix && (
                          <div className="flex space-x-2">
                            {Object.entries(testScenario.media_mix).map(([channel, config]: [string, any]) => (
                              <span key={channel} className="bg-gray-100 px-2 py-1 rounded">
                                {channel}: {(config.share * 100).toFixed(0)}%
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {selectedScenario && (
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h6 className="font-medium text-purple-900 mb-2">テスト設計提案</h6>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-purple-700 font-medium">推奨サンプルサイズ:</span>
                        <div>各バリアント 5,000 ユーザー以上</div>
                      </div>
                      <div>
                        <span className="text-purple-700 font-medium">テスト期間:</span>
                        <div>最低 14日間（2週間）</div>
                      </div>
                      <div>
                        <span className="text-purple-700 font-medium">主要指標:</span>
                        <div>コンバージョン率、ROI</div>
                      </div>
                      <div>
                        <span className="text-purple-700 font-medium">有意水準:</span>
                        <div>95%信頼区間</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};