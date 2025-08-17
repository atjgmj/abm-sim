import React, { useState } from 'react';
import { 
  Target, 
  Brain, 
  BarChart3, 
  Users, 
  Network, 
  Zap,
  Shield,
  Clock,
  TrendingUp,
  Database,
  Settings,
  CheckCircle,
  AlertTriangle,
  Info,
  DollarSign,
  Lightbulb,
  BookOpen,
  GitBranch,
  Activity
} from 'lucide-react';

export const ProductOverview: React.FC = () => {
  const [activeSection, setActiveSection] = useState<'overview' | 'theory' | 'features' | 'technical' | 'roi'>('overview');

  const useCases = [
    {
      title: "マーケティング効果予測",
      description: "キャンペーン実施前に効果を定量的に予測",
      benefits: ["ROI最大化", "リスク軽減", "予算配分最適化"]
    },
    {
      title: "メディアミックス最適化", 
      description: "SNS・動画・検索広告の最適な配分を決定",
      benefits: ["コスト効率向上", "リーチ最大化", "ターゲット精度向上"]
    },
    {
      title: "口コミ拡散戦略",
      description: "インフルエンサーとWoM効果の最適活用",
      benefits: ["バイラル効果", "信頼性向上", "長期的ブランド価値"]
    },
    {
      title: "A/Bテスト設計",
      description: "統計的に有意なテスト設計と効果検証",
      benefits: ["意思決定支援", "継続改善", "データドリブン経営"]
    }
  ];

  const features = [
    {
      icon: Brain,
      title: "AI/ML最適化",
      description: "過去データを学習し、最適なパラメータを自動提案",
      details: ["Random Forest回帰", "Bayesian最適化", "交差検証"]
    },
    {
      icon: Network,
      title: "ネットワーク分析",
      description: "顧客間の影響関係をモデル化",
      details: ["3種類のネットワーク", "影響力分析", "拡散経路可視化"]
    },
    {
      icon: BarChart3,
      title: "リアルタイム分析",
      description: "シミュレーション結果の即座な可視化",
      details: ["時系列チャート", "KPI追跡", "CSV出力"]
    },
    {
      icon: Users,
      title: "競合分析",
      description: "業界データに基づく競合ポジション分析",
      details: ["市場シェア分析", "戦略提案", "機会発見"]
    }
  ];

  const technicalSpecs = [
    {
      category: "アーキテクチャ",
      items: [
        "FastAPI + React フルスタック",
        "Mesa ABMフレームワーク",
        "SQLite データストア",
        "リアルタイム処理"
      ]
    },
    {
      category: "ML技術スタック",
      items: [
        "scikit-learn (RandomForest, GradientBoosting)",
        "Optuna Bayesian最適化",
        "NumPy/Pandas データ処理",
        "完全ローカル実行（APIキー不要）"
      ]
    },
    {
      category: "スケーラビリティ",
      items: [
        "最大100,000ノード対応",
        "並列シミュレーション実行",
        "バックグラウンド処理",
        "自動リソース管理"
      ]
    },
    {
      category: "セキュリティ",
      items: [
        "ローカル環境完結",
        "データ外部送信なし",
        "セキュアな設計",
        "監査証跡記録"
      ]
    }
  ];

  const roiMetrics = [
    {
      metric: "意思決定速度",
      improvement: "75%短縮",
      description: "キャンペーン計画から実行まで"
    },
    {
      metric: "予算効率",
      improvement: "30%向上",
      description: "最適化されたメディアミックス"
    },
    {
      metric: "リスク軽減",
      improvement: "60%削減",
      description: "事前シミュレーションによる失敗防止"
    },
    {
      metric: "ROI向上",
      improvement: "25%増加",
      description: "データドリブンな戦略決定"
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center bg-gradient-to-r from-blue-50 to-purple-50 p-8 rounded-lg">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          ABM Communication Campaign Simulator
        </h2>
        <p className="text-xl text-gray-600 mb-6">
          エージェントベースモデリングによる次世代マーケティング最適化プラットフォーム
        </p>
        <div className="flex justify-center space-x-4">
          <div className="bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium">
            <CheckCircle className="h-4 w-4 inline mr-2" />
            即座に導入可能
          </div>
          <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium">
            <Shield className="h-4 w-4 inline mr-2" />
            完全ローカル実行
          </div>
          <div className="bg-purple-100 text-purple-800 px-4 py-2 rounded-full text-sm font-medium">
            <Brain className="h-4 w-4 inline mr-2" />
            AI/ML搭載
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'overview', label: '導入目的・効果', icon: Target },
            { id: 'theory', label: '理論・手法', icon: BookOpen },
            { id: 'features', label: '主要機能', icon: Settings },
            { id: 'technical', label: '技術仕様', icon: Database },
            { id: 'roi', label: 'ROI・効果測定', icon: DollarSign },
          ].map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveSection(tab.id as any)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeSection === tab.id
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

      {/* Content */}
      {activeSection === 'overview' && (
        <div className="space-y-8">
          {/* Problem Statement */}
          <div className="bg-red-50 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-red-900 mb-4 flex items-center">
              <AlertTriangle className="h-6 w-6 mr-2" />
              現在のマーケティングの課題
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center text-red-800">
                  <span className="w-2 h-2 bg-red-600 rounded-full mr-3"></span>
                  キャンペーン効果の事前予測が困難
                </div>
                <div className="flex items-center text-red-800">
                  <span className="w-2 h-2 bg-red-600 rounded-full mr-3"></span>
                  最適なメディアミックスが不明
                </div>
                <div className="flex items-center text-red-800">
                  <span className="w-2 h-2 bg-red-600 rounded-full mr-3"></span>
                  口コミ効果の定量化が不可能
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center text-red-800">
                  <span className="w-2 h-2 bg-red-600 rounded-full mr-3"></span>
                  高額な失敗コストリスク
                </div>
                <div className="flex items-center text-red-800">
                  <span className="w-2 h-2 bg-red-600 rounded-full mr-3"></span>
                  A/Bテストの設計ノウハウ不足
                </div>
                <div className="flex items-center text-red-800">
                  <span className="w-2 h-2 bg-red-600 rounded-full mr-3"></span>
                  データドリブンな意思決定の難しさ
                </div>
              </div>
            </div>
          </div>

          {/* Solution */}
          <div className="bg-green-50 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-green-900 mb-4 flex items-center">
              <Lightbulb className="h-6 w-6 mr-2" />
              ABMシミュレータによる解決
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center text-green-800">
                  <CheckCircle className="h-5 w-5 mr-3 text-green-600" />
                  事前シミュレーションで効果を定量予測
                </div>
                <div className="flex items-center text-green-800">
                  <CheckCircle className="h-5 w-5 mr-3 text-green-600" />
                  AI/MLによる最適パラメータ自動提案
                </div>
                <div className="flex items-center text-green-800">
                  <CheckCircle className="h-5 w-5 mr-3 text-green-600" />
                  ネットワーク効果の可視化・分析
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center text-green-800">
                  <CheckCircle className="h-5 w-5 mr-3 text-green-600" />
                  リスクのない仮想環境でのテスト
                </div>
                <div className="flex items-center text-green-800">
                  <CheckCircle className="h-5 w-5 mr-3 text-green-600" />
                  統計的に有意なA/Bテスト設計
                </div>
                <div className="flex items-center text-green-800">
                  <CheckCircle className="h-5 w-5 mr-3 text-green-600" />
                  証拠に基づく戦略的意思決定
                </div>
              </div>
            </div>
          </div>

          {/* Use Cases */}
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-6">主要活用シーン</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {useCases.map((useCase, idx) => (
                <div key={idx} className="bg-white p-6 rounded-lg border shadow-sm">
                  <h4 className="text-lg font-semibold text-gray-900 mb-3">{useCase.title}</h4>
                  <p className="text-gray-600 mb-4">{useCase.description}</p>
                  <div className="space-y-2">
                    {useCase.benefits.map((benefit, benefitIdx) => (
                      <div key={benefitIdx} className="flex items-center text-sm text-blue-700">
                        <TrendingUp className="h-4 w-4 mr-2" />
                        {benefit}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeSection === 'theory' && (
        <div className="space-y-8">
          {/* ABM Theory Overview */}
          <div className="bg-blue-50 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-blue-900 mb-4 flex items-center">
              <BookOpen className="h-6 w-6 mr-2" />
              エージェントベースモデリング（ABM）とは
            </h3>
            <p className="text-blue-800 mb-4">
              ABMは、個々のエージェント（顧客）の行動とその相互作用をモデル化し、
              全体のシステム挙動を創発的に生成する計算社会科学の手法です。
              従来の統計モデルでは捉えられない複雑な社会現象を再現可能にします。
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg">
                <Users className="h-8 w-8 text-blue-600 mb-2" />
                <h4 className="font-semibold text-blue-900 mb-2">個別エージェント</h4>
                <p className="text-sm text-blue-700">各顧客を独立したエージェントとしてモデル化</p>
              </div>
              <div className="bg-white p-4 rounded-lg">
                <Network className="h-8 w-8 text-blue-600 mb-2" />
                <h4 className="font-semibold text-blue-900 mb-2">相互作用</h4>
                <p className="text-sm text-blue-700">エージェント間の影響関係を動的にシミュレーション</p>
              </div>
              <div className="bg-white p-4 rounded-lg">
                <Activity className="h-8 w-8 text-blue-600 mb-2" />
                <h4 className="font-semibold text-blue-900 mb-2">創発現象</h4>
                <p className="text-sm text-blue-700">個別行動から全体の複雑なパターンが自然発生</p>
              </div>
            </div>
          </div>

          {/* Demographic Theory */}
          <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg mb-8">
            <h3 className="text-xl font-bold text-green-900 mb-4 flex items-center">
              <Users className="h-6 w-6 mr-2" />
              人口統計学的パラメータの理論的基盤
            </h3>
            <p className="text-green-800 mb-6">
              本システムでは、個々の顧客エージェントが多次元の人口統計学的特性を持ち、
              これらがメディア受容性、社会的影響力、購買行動に複合的に影響します。
              Rogers の拡散理論を基盤とした心理学的プロファイルと人口統計学的属性の統合モデルを採用しています。
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white p-5 rounded-lg">
                <h4 className="font-semibold text-green-800 mb-3 flex items-center">
                  <Target className="h-4 w-4 mr-2" />
                  人口統計学的属性
                </h4>
                <div className="space-y-3 text-sm">
                  <div>
                    <strong className="text-blue-700">年齢層 (Age Group)</strong>
                    <div className="text-gray-600 mt-1">1-5スケール（若年〜高齢）</div>
                    <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded mt-1">
                      影響: メディア親和性、リスク許容度、新商品への開放性
                    </div>
                  </div>
                  <div>
                    <strong className="text-blue-700">所得レベル (Income Level)</strong>
                    <div className="text-gray-600 mt-1">1-5スケール（低所得〜高所得）</div>
                    <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded mt-1">
                      影響: 購買力、検索広告反応性、社会的影響力
                    </div>
                  </div>
                  <div>
                    <strong className="text-blue-700">都市部-地方 (Urban-Rural)</strong>
                    <div className="text-gray-600 mt-1">連続値 [0,1]（地方〜都市部）</div>
                    <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded mt-1">
                      影響: メディア接触機会、ネットワーク密度、情報感度
                    </div>
                  </div>
                  <div>
                    <strong className="text-blue-700">教育レベル (Education)</strong>
                    <div className="text-gray-600 mt-1">1-5スケール（基礎〜大学院）</div>
                    <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded mt-1">
                      影響: 情報処理能力、検索行動、批判的思考
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white p-5 rounded-lg">
                <h4 className="font-semibold text-green-800 mb-3 flex items-center">
                  <Brain className="h-4 w-4 mr-2" />
                  性格特性 (Rogers拡散理論)
                </h4>
                <div className="space-y-3 text-sm">
                  <div>
                    <strong className="text-purple-700">イノベーター (2.5%)</strong>
                    <div className="text-xs text-gray-500 bg-purple-50 p-2 rounded mt-1">
                      高開放性、低社会影響、高リスク許容度
                    </div>
                  </div>
                  <div>
                    <strong className="text-blue-700">アーリーアダプター (13.5%)</strong>
                    <div className="text-xs text-gray-500 bg-blue-50 p-2 rounded mt-1">
                      中高開放性、中低社会影響、中高リスク許容度
                    </div>
                  </div>
                  <div>
                    <strong className="text-green-700">アーリーマジョリティ (34%)</strong>
                    <div className="text-xs text-gray-500 bg-green-50 p-2 rounded mt-1">
                      中開放性、中高社会影響、中リスク許容度
                    </div>
                  </div>
                  <div>
                    <strong className="text-yellow-700">レイトマジョリティ (34%)</strong>
                    <div className="text-xs text-gray-500 bg-yellow-50 p-2 rounded mt-1">
                      中低開放性、高社会影響、中低リスク許容度
                    </div>
                  </div>
                  <div>
                    <strong className="text-red-700">ラガード (16%)</strong>
                    <div className="text-xs text-gray-500 bg-red-50 p-2 rounded mt-1">
                      低開放性、非常に高い社会影響、低リスク許容度
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Parameter Integration Model */}
          <div className="bg-white p-6 rounded-lg border shadow-sm mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
              <GitBranch className="h-6 w-6 text-indigo-600 mr-2" />
              パラメータ統合モデル
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-800 mb-3">関心度計算式</h4>
                <div className="text-sm space-y-2">
                  <div className="bg-white p-2 rounded font-mono text-xs">
                    Interest = Openness×0.6 + Risk×0.4 + Age_factor×0.2 + Education×0.1
                  </div>
                  <div className="text-blue-700">
                    <strong>Age_factor:</strong> (6-年齢層)/5 × 0.2<br/>
                    <strong>Education:</strong> 教育レベル/5 × 0.1
                  </div>
                </div>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-semibold text-green-800 mb-3">受容性計算式</h4>
                <div className="text-sm space-y-2">
                  <div className="bg-white p-2 rounded font-mono text-xs">
                    Receptivity = Media_Affinity×0.7 + Openness×0.3 + Urban×0.1
                  </div>
                  <div className="text-green-700">
                    <strong>Media_Affinity:</strong> メディア親和性 [0,1]<br/>
                    <strong>Urban:</strong> 都市部度 × 0.1
                  </div>
                </div>
              </div>
              
              <div className="bg-purple-50 p-4 rounded-lg">
                <h4 className="font-semibold text-purple-800 mb-3">影響力計算式</h4>
                <div className="text-sm space-y-2">
                  <div className="bg-white p-2 rounded font-mono text-xs">
                    Influence = Social×0.4 + Education×0.3 + Income×0.3
                  </div>
                  <div className="text-purple-700">
                    <strong>Social:</strong> 社会的影響性<br/>
                    <strong>インフルエンサー:</strong> ×3.0倍率
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold text-gray-800 mb-2">チャネル別人口統計学調整</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <strong className="text-blue-600">SNS チャネル:</strong>
                  <div className="text-gray-600 mt-1">
                    • 年齢: 若年層 +50%効果<br/>
                    • 都市部: +30%露出確率<br/>
                    • 教育: 高学歴 +30%
                  </div>
                </div>
                <div>
                  <strong className="text-red-600">動画チャネル:</strong>
                  <div className="text-gray-600 mt-1">
                    • 年齢: 若年層 +30%<br/>
                    • 所得: 高所得 +20%<br/>
                    • より普遍的な訴求
                  </div>
                </div>
                <div>
                  <strong className="text-green-600">検索チャネル:</strong>
                  <div className="text-gray-600 mt-1">
                    • 教育: +40%効果<br/>
                    • 所得: +30%効果<br/>
                    • 能動的な情報探索
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Parameter Impact Analysis */}
          <div className="bg-gradient-to-r from-orange-50 to-red-50 p-6 rounded-lg mb-8">
            <h3 className="text-xl font-bold text-orange-900 mb-4 flex items-center">
              <BarChart3 className="h-6 w-6 mr-2" />
              パラメータ影響度分析
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white p-5 rounded-lg">
                <h4 className="font-semibold text-orange-800 mb-3">関心度への影響重み</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Openness（開放性）</span>
                    <div className="flex items-center">
                      <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                        <div className="bg-blue-600 h-2 rounded-full" style={{width: '60%'}}></div>
                      </div>
                      <span className="text-xs font-mono">60%</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Risk Tolerance（リスク許容度）</span>
                    <div className="flex items-center">
                      <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                        <div className="bg-green-600 h-2 rounded-full" style={{width: '40%'}}></div>
                      </div>
                      <span className="text-xs font-mono">40%</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Age Factor（年齢要因）</span>
                    <div className="flex items-center">
                      <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                        <div className="bg-yellow-600 h-2 rounded-full" style={{width: '20%'}}></div>
                      </div>
                      <span className="text-xs font-mono">20%</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Education（教育レベル）</span>
                    <div className="flex items-center">
                      <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                        <div className="bg-purple-600 h-2 rounded-full" style={{width: '10%'}}></div>
                      </div>
                      <span className="text-xs font-mono">10%</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white p-5 rounded-lg">
                <h4 className="font-semibold text-orange-800 mb-3">メディア受容性への影響重み</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Media Affinity（メディア親和性）</span>
                    <div className="flex items-center">
                      <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                        <div className="bg-blue-600 h-2 rounded-full" style={{width: '70%'}}></div>
                      </div>
                      <span className="text-xs font-mono">70%</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Openness（開放性）</span>
                    <div className="flex items-center">
                      <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                        <div className="bg-green-600 h-2 rounded-full" style={{width: '30%'}}></div>
                      </div>
                      <span className="text-xs font-mono">30%</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Urban Factor（都市部要因）</span>
                    <div className="flex items-center">
                      <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                        <div className="bg-yellow-600 h-2 rounded-full" style={{width: '10%'}}></div>
                      </div>
                      <span className="text-xs font-mono">10%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-6 bg-white p-5 rounded-lg">
              <h4 className="font-semibold text-orange-800 mb-3">社会的影響力への影響重み</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Social Influence</span>
                  <div className="flex items-center">
                    <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                      <div className="bg-purple-600 h-2 rounded-full" style={{width: '40%'}}></div>
                    </div>
                    <span className="text-xs font-mono">40%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Education</span>
                  <div className="flex items-center">
                    <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                      <div className="bg-blue-600 h-2 rounded-full" style={{width: '30%'}}></div>
                    </div>
                    <span className="text-xs font-mono">30%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Income</span>
                  <div className="flex items-center">
                    <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                      <div className="bg-green-600 h-2 rounded-full" style={{width: '30%'}}></div>
                    </div>
                    <span className="text-xs font-mono">30%</span>
                  </div>
                </div>
              </div>
              <div className="mt-4 p-3 bg-orange-50 rounded text-sm">
                <strong>インフルエンサー倍率:</strong> 通常の影響力 × 3.0倍（インフルエンサー判定時）
              </div>
            </div>
          </div>

          {/* Network Simulation Details */}
          <div className="bg-gradient-to-r from-cyan-50 to-blue-50 p-6 rounded-lg mb-8">
            <h3 className="text-xl font-bold text-cyan-900 mb-4 flex items-center">
              <Network className="h-6 w-6 mr-2" />
              ネットワーク理論とシミュレーション実装
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-white p-5 rounded-lg">
                <h4 className="font-semibold text-cyan-800 mb-3 flex items-center">
                  <span className="w-3 h-3 bg-orange-500 rounded-full mr-2"></span>
                  Erdős-Rényi
                </h4>
                <div className="text-sm space-y-2">
                  <div className="bg-orange-50 p-2 rounded text-xs font-mono">
                    P(edge) = k/(n-1)<br/>
                    ⟨k⟩ = np
                  </div>
                  <div className="text-gray-700">
                    <strong>特徴:</strong> 均質なランダム接続<br/>
                    <strong>用途:</strong> 基本的な情報拡散モデル<br/>
                    <strong>WoM特性:</strong> 均等な拡散速度
                  </div>
                  <div className="bg-gray-50 p-2 rounded text-xs">
                    <strong>実装:</strong> NetworkX.erdos_renyi_graph(n, p)<br/>
                    <strong>パラメータ:</strong> n=ノード数, p=接続確率
                  </div>
                </div>
              </div>
              
              <div className="bg-white p-5 rounded-lg">
                <h4 className="font-semibold text-cyan-800 mb-3 flex items-center">
                  <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
                  Watts-Strogatz
                </h4>
                <div className="text-sm space-y-2">
                  <div className="bg-blue-50 p-2 rounded text-xs font-mono">
                    C &gt;&gt; C_random<br/>
                    L ≈ L_random
                  </div>
                  <div className="text-gray-700">
                    <strong>特徴:</strong> 高クラスタ化 + 短経路<br/>
                    <strong>用途:</strong> 現実的な社会ネットワーク<br/>
                    <strong>WoM特性:</strong> クラスタ内高密度拡散
                  </div>
                  <div className="bg-gray-50 p-2 rounded text-xs">
                    <strong>実装:</strong> NetworkX.watts_strogatz_graph(n, k, p)<br/>
                    <strong>パラメータ:</strong> k=近傍数, p=再配線確率
                  </div>
                </div>
              </div>
              
              <div className="bg-white p-5 rounded-lg">
                <h4 className="font-semibold text-cyan-800 mb-3 flex items-center">
                  <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                  Barabási-Albert
                </h4>
                <div className="text-sm space-y-2">
                  <div className="bg-green-50 p-2 rounded text-xs font-mono">
                    P(k) ∝ k⁻ᵞ<br/>
                    γ ≈ 3
                  </div>
                  <div className="text-gray-700">
                    <strong>特徴:</strong> ハブノード存在<br/>
                    <strong>用途:</strong> インフルエンサー効果<br/>
                    <strong>WoM特性:</strong> 急速な情報拡散
                  </div>
                  <div className="bg-gray-50 p-2 rounded text-xs">
                    <strong>実装:</strong> NetworkX.barabasi_albert_graph(n, m)<br/>
                    <strong>パラメータ:</strong> m=優先接続数
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-5 rounded-lg">
              <h4 className="font-semibold text-cyan-800 mb-3">WoM拡散アルゴリズム詳細</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h5 className="font-medium text-cyan-700 mb-2">Step 1: WoM生成判定</h5>
                  <div className="text-sm bg-cyan-50 p-3 rounded space-y-1">
                    <div className="font-mono text-xs">for neighbor in network.neighbors(agent_id):</div>
                    <div className="font-mono text-xs ml-4">if neighbor.state &gt;= LIKING:</div>
                    <div className="font-mono text-xs ml-8">wom_prob = p_generate × influence × 0.1</div>
                    <div className="font-mono text-xs ml-8">wom_prob *= (1 + similarity_bonus)</div>
                    <div className="text-gray-600 mt-2">
                      <strong>条件:</strong> 好意状態以上のエージェントが発信<br/>
                      <strong>確率:</strong> 影響力と類似性に比例
                    </div>
                  </div>
                </div>
                
                <div>
                  <h5 className="font-medium text-cyan-700 mb-2">Step 2: WoM効果計算</h5>
                  <div className="text-sm bg-cyan-50 p-3 rounded space-y-1">
                    <div className="font-mono text-xs">base_effect = 0.05 × current_receptivity</div>
                    <div className="font-mono text-xs">social_factor = personality['social_influence']</div>
                    <div className="font-mono text-xs">influencer_factor = 2.0 if is_influencer else 1.0</div>
                    <div className="font-mono text-xs">effect_prob = base_effect × social_factor × influencer_factor</div>
                    <div className="text-gray-600 mt-2">
                      <strong>要因:</strong> 受容性 × 社会的影響性 × インフルエンサー効果
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 p-3 bg-gray-50 rounded">
                <h5 className="font-medium text-gray-800 mb-2">類似性ボーナス計算</h5>
                <div className="text-sm font-mono text-gray-700">
                  age_similarity = max(0, 1 - |age_diff| / 4.0)<br/>
                  income_similarity = max(0, 1 - |income_diff| / 4.0)<br/>
                  urban_similarity = max(0, 1 - |urban_diff|)<br/>
                  similarity_bonus = (age_sim × 0.4 + income_sim × 0.3 + urban_sim × 0.3) × 0.3
                </div>
              </div>
            </div>
          </div>

          {/* Core Models */}
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-6">コアモデル理論</h3>
            <div className="space-y-6">
              
              {/* Customer Agent Model */}
              <div className="bg-white p-6 rounded-lg border shadow-sm">
                <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Users className="h-5 w-5 text-green-600 mr-2" />
                  顧客エージェントモデル
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h5 className="font-medium text-gray-800 mb-3">状態変数（KPI）</h5>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center">
                        <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
                        <strong>Awareness</strong>: ブランド認知度 [0,1]
                      </div>
                      <div className="flex items-center">
                        <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                        <strong>Interest</strong>: 関心度 [0,1]
                      </div>
                      <div className="flex items-center">
                        <span className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></span>
                        <strong>Knowledge</strong>: 知識レベル [0,1]
                      </div>
                      <div className="flex items-center">
                        <span className="w-3 h-3 bg-red-500 rounded-full mr-2"></span>
                        <strong>Liking</strong>: 好意度 [0,1]
                      </div>
                      <div className="flex items-center">
                        <span className="w-3 h-3 bg-purple-500 rounded-full mr-2"></span>
                        <strong>Intent</strong>: 購買意向 [0,1]
                      </div>
                    </div>
                  </div>
                  <div>
                    <h5 className="font-medium text-gray-800 mb-3">個人特性</h5>
                    <div className="space-y-2 text-sm">
                      <div><strong>Openness</strong>: 新しい体験への開放性</div>
                      <div><strong>Social Influence</strong>: 社会的影響の受けやすさ</div>
                      <div><strong>Media Affinity</strong>: メディア消費傾向</div>
                      <div><strong>Risk Tolerance</strong>: リスク許容度</div>
                    </div>
                  </div>
                </div>
                <div className="mt-4 p-3 bg-gray-50 rounded text-sm">
                  <strong>状態遷移式:</strong> S<sub>t+1</sub> = f(S<sub>t</sub>, Media<sub>t</sub>, WoM<sub>t</sub>, Personal<sub>i</sub>, Demo<sub>i</sub>)
                </div>
              </div>

              {/* Communication Model */}
              <div className="bg-white p-6 rounded-lg border shadow-sm">
                <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <BarChart3 className="h-5 w-5 text-blue-600 mr-2" />
                  コミュニケーションモデル
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h5 className="font-medium text-gray-800 mb-3">メディア効果式</h5>
                    <div className="space-y-2 text-sm bg-gray-50 p-3 rounded">
                      <div><strong>Adstock効果:</strong> A<sub>t</sub> = α × M<sub>t</sub> + β × A<sub>t-1</sub></div>
                      <div><strong>Saturation効果:</strong> E = 1 - exp(-γ × A<sub>t</sub>)</div>
                      <div><strong>α:</strong> 即時効果係数</div>
                      <div><strong>β:</strong> 継続効果係数（減衰率）</div>
                      <div><strong>γ:</strong> 飽和効果係数</div>
                    </div>
                  </div>
                  <div>
                    <h5 className="font-medium text-gray-800 mb-3">メディアチャネル</h5>
                    <div className="space-y-2 text-sm">
                      <div><strong>SNS:</strong> 高いバイラル性、若年層効果</div>
                      <div><strong>動画:</strong> 高いエンゲージメント、視覚的訴求</div>
                      <div><strong>検索:</strong> 購買直前の効果、ロングテール</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* WoM Model */}
              <div className="bg-white p-6 rounded-lg border shadow-sm">
                <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <GitBranch className="h-5 w-5 text-purple-600 mr-2" />
                  口コミ（WoM）拡散モデル
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h5 className="font-medium text-gray-800 mb-3">拡散メカニズム</h5>
                    <div className="space-y-2 text-sm">
                      <div><strong>発生確率:</strong> P(generate) = p × Engagement<sub>i</sub></div>
                      <div><strong>伝播確率:</strong> P(transmit) = Influence<sub>i→j</sub> × Receptivity<sub>j</sub></div>
                      <div><strong>減衰効果:</strong> WoM<sub>t+1</sub> = decay × WoM<sub>t</sub></div>
                    </div>
                  </div>
                  <div>
                    <h5 className="font-medium text-gray-800 mb-3">ネットワーク構造</h5>
                    <div className="space-y-2 text-sm">
                      <div><strong>Erdős-Rényi:</strong> ランダムネットワーク</div>
                      <div><strong>Watts-Strogatz:</strong> スモールワールド</div>
                      <div><strong>Barabási-Albert:</strong> スケールフリー</div>
                    </div>
                  </div>
                </div>
                <div className="mt-4 p-3 bg-purple-50 rounded text-sm">
                  <strong>インフルエンサー効果:</strong> 高影響力ノードが少数存在し、拡散を加速
                </div>
              </div>

              {/* Network Theory */}
              <div className="bg-white p-6 rounded-lg border shadow-sm">
                <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Network className="h-5 w-5 text-orange-600 mr-2" />
                  ネットワーク理論
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-orange-50 p-4 rounded">
                    <h5 className="font-semibold text-orange-800 mb-2">Erdős-Rényi</h5>
                    <p className="text-xs text-orange-700 mb-2">ランダムグラフ理論</p>
                    <div className="text-xs text-orange-600">
                      <div>P(edge) = p = k/(n-1)</div>
                      <div>平均次数: ⟨k⟩ = np</div>
                    </div>
                  </div>
                  <div className="bg-blue-50 p-4 rounded">
                    <h5 className="font-semibold text-blue-800 mb-2">Watts-Strogatz</h5>
                    <p className="text-xs text-blue-700 mb-2">スモールワールド</p>
                    <div className="text-xs text-blue-600">
                      <div>再配線確率: β</div>
                      <div>クラスタ係数 + 短い経路長</div>
                    </div>
                  </div>
                  <div className="bg-green-50 p-4 rounded">
                    <h5 className="font-semibold text-green-800 mb-2">Barabási-Albert</h5>
                    <p className="text-xs text-green-700 mb-2">スケールフリー</p>
                    <div className="text-xs text-green-600">
                      <div>優先的接続メカニズム</div>
                      <div>次数分布: P(k) ∝ k<sup>-γ</sup></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* ML Theory */}
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-purple-900 mb-4 flex items-center">
              <Brain className="h-6 w-6 mr-2" />
              機械学習最適化理論
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-purple-800 mb-3">教師あり学習モデル</h4>
                <div className="space-y-2 text-sm text-purple-700">
                  <div><strong>Random Forest:</strong> 決定木アンサンブル、特徴量重要度</div>
                  <div><strong>Gradient Boosting:</strong> 勾配ブースティング、非線形関係</div>
                  <div><strong>Gaussian Process:</strong> 不確実性定量化、ベイジアン推論</div>
                </div>
              </div>
              <div>
                <h4 className="font-semibold text-purple-800 mb-3">ベイジアン最適化</h4>
                <div className="space-y-2 text-sm text-purple-700">
                  <div><strong>Objective:</strong> max f(x) where f is expensive</div>
                  <div><strong>Acquisition:</strong> Expected Improvement, UCB</div>
                  <div><strong>Surrogate Model:</strong> GP回帰による関数近似</div>
                </div>
              </div>
            </div>
            <div className="mt-4 p-3 bg-white rounded text-sm">
              <strong>最適化プロセス:</strong> 
              Historical Data → Feature Engineering → ML Training → Bayesian Optimization → Parameter Recommendation
            </div>
          </div>

          {/* Academic Foundation */}
          <div className="bg-gray-50 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-gray-900 mb-4">学術的基盤</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-800 mb-3">理論的基礎</h4>
                <ul className="space-y-1 text-sm text-gray-700">
                  <li>• 複雑系科学（Complex Systems Science）</li>
                  <li>• 計算社会科学（Computational Social Science）</li>
                  <li>• ネットワーク理論（Graph Theory）</li>
                  <li>• 拡散理論（Diffusion of Innovation）</li>
                  <li>• 機械学習理論（Statistical Learning Theory）</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-800 mb-3">応用分野</h4>
                <ul className="space-y-1 text-sm text-gray-700">
                  <li>• マーケティングサイエンス</li>
                  <li>• 消費者行動分析</li>
                  <li>• ソーシャルネットワーク分析</li>
                  <li>• メディアミックス最適化</li>
                  <li>• バイラルマーケティング</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeSection === 'features' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <div key={idx} className="bg-white p-6 rounded-lg border shadow-sm">
                  <div className="flex items-center mb-4">
                    <Icon className="h-8 w-8 text-blue-600 mr-3" />
                    <h3 className="text-xl font-semibold text-gray-900">{feature.title}</h3>
                  </div>
                  <p className="text-gray-600 mb-4">{feature.description}</p>
                  <div className="space-y-2">
                    {feature.details.map((detail, detailIdx) => (
                      <div key={detailIdx} className="flex items-center text-sm text-gray-700">
                        <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                        {detail}
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Feature Matrix */}
          <div className="bg-gray-50 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-gray-900 mb-6">機能比較マトリクス</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-semibold text-gray-900">機能</th>
                    <th className="text-center py-3 px-4 font-semibold text-gray-900">従来手法</th>
                    <th className="text-center py-3 px-4 font-semibold text-gray-900">ABMシミュレータ</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  <tr>
                    <td className="py-3 px-4 font-medium">効果予測</td>
                    <td className="py-3 px-4 text-center text-red-600">経験・勘に依存</td>
                    <td className="py-3 px-4 text-center text-green-600">定量的シミュレーション</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 font-medium">最適化</td>
                    <td className="py-3 px-4 text-center text-red-600">試行錯誤</td>
                    <td className="py-3 px-4 text-center text-green-600">AI/ML自動最適化</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 font-medium">リスク</td>
                    <td className="py-3 px-4 text-center text-red-600">高額な失敗コスト</td>
                    <td className="py-3 px-4 text-center text-green-600">仮想環境でのテスト</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 font-medium">スピード</td>
                    <td className="py-3 px-4 text-center text-red-600">数週間〜数ヶ月</td>
                    <td className="py-3 px-4 text-center text-green-600">数分〜数時間</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeSection === 'technical' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {technicalSpecs.map((spec, idx) => (
              <div key={idx} className="bg-white p-6 rounded-lg border shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">{spec.category}</h3>
                <div className="space-y-3">
                  {spec.items.map((item, itemIdx) => (
                    <div key={itemIdx} className="flex items-center text-sm text-gray-700">
                      <CheckCircle className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />
                      {item}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* System Requirements */}
          <div className="bg-blue-50 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-blue-900 mb-4">システム要件</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h4 className="font-semibold text-blue-800 mb-2">最小要件</h4>
                <ul className="space-y-1 text-sm text-blue-700">
                  <li>• CPU: 4コア以上</li>
                  <li>• RAM: 8GB以上</li>
                  <li>• ストレージ: 10GB</li>
                  <li>• OS: Windows/Mac/Linux</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-blue-800 mb-2">推奨環境</h4>
                <ul className="space-y-1 text-sm text-blue-700">
                  <li>• CPU: 8コア以上</li>
                  <li>• RAM: 16GB以上</li>
                  <li>• ストレージ: SSD 20GB</li>
                  <li>• ネットワーク: 高速回線</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-blue-800 mb-2">セキュリティ</h4>
                <ul className="space-y-1 text-sm text-blue-700">
                  <li>• ローカル実行</li>
                  <li>• データ外部送信なし</li>
                  <li>• 暗号化ストレージ</li>
                  <li>• アクセス制御</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeSection === 'roi' && (
        <div className="space-y-8">
          {/* ROI Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {roiMetrics.map((metric, idx) => (
              <div key={idx} className="bg-gradient-to-br from-green-50 to-blue-50 p-6 rounded-lg text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">{metric.improvement}</div>
                <div className="text-lg font-semibold text-gray-900 mb-2">{metric.metric}</div>
                <div className="text-sm text-gray-600">{metric.description}</div>
              </div>
            ))}
          </div>

          {/* Cost Analysis */}
          <div className="bg-white p-6 rounded-lg border shadow-sm">
            <h3 className="text-xl font-bold text-gray-900 mb-6">コスト分析</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h4 className="font-semibold text-gray-900 mb-4">従来のマーケティング失敗コスト</h4>
                <div className="space-y-3">
                  <div className="flex justify-between items-center py-2 border-b border-gray-200">
                    <span className="text-gray-600">キャンペーン失敗（年1回）</span>
                    <span className="font-semibold text-red-600">¥50,000,000</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-gray-200">
                    <span className="text-gray-600">非効率な予算配分</span>
                    <span className="font-semibold text-red-600">¥20,000,000</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-gray-200">
                    <span className="text-gray-600">意思決定遅延コスト</span>
                    <span className="font-semibold text-red-600">¥10,000,000</span>
                  </div>
                  <div className="flex justify-between items-center py-2 font-bold text-lg">
                    <span>年間潜在損失</span>
                    <span className="text-red-600">¥80,000,000</span>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-4">ABMシミュレータ導入効果</h4>
                <div className="space-y-3">
                  <div className="flex justify-between items-center py-2 border-b border-gray-200">
                    <span className="text-gray-600">失敗リスク軽減効果</span>
                    <span className="font-semibold text-green-600">¥30,000,000</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-gray-200">
                    <span className="text-gray-600">予算効率向上効果</span>
                    <span className="font-semibold text-green-600">¥6,000,000</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-gray-200">
                    <span className="text-gray-600">意思決定高速化効果</span>
                    <span className="font-semibold text-green-600">¥7,500,000</span>
                  </div>
                  <div className="flex justify-between items-center py-2 font-bold text-lg">
                    <span>年間効果</span>
                    <span className="text-green-600">¥43,500,000</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Implementation Timeline */}
          <div className="bg-gray-50 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-gray-900 mb-6">導入タイムライン</h3>
            <div className="space-y-4">
              <div className="flex items-center">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold text-sm">1</div>
                <div className="ml-4">
                  <div className="font-semibold">環境構築・インストール</div>
                  <div className="text-sm text-gray-600">システム要件確認、ソフトウェアインストール</div>
                  <div className="text-xs text-blue-600 mt-1">所要時間: 1-2日</div>
                </div>
              </div>
              <div className="flex items-center">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold text-sm">2</div>
                <div className="ml-4">
                  <div className="font-semibold">基本操作トレーニング</div>
                  <div className="text-sm text-gray-600">シナリオ作成、シミュレーション実行、結果分析</div>
                  <div className="text-xs text-blue-600 mt-1">所要時間: 3-5日</div>
                </div>
              </div>
              <div className="flex items-center">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold text-sm">3</div>
                <div className="ml-4">
                  <div className="font-semibold">実データでの検証</div>
                  <div className="text-sm text-gray-600">過去キャンペーンデータでの精度検証</div>
                  <div className="text-xs text-blue-600 mt-1">所要時間: 1-2週間</div>
                </div>
              </div>
              <div className="flex items-center">
                <div className="flex-shrink-0 w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center font-bold text-sm">4</div>
                <div className="ml-4">
                  <div className="font-semibold">本格運用開始</div>
                  <div className="text-sm text-gray-600">実際のキャンペーン計画での活用開始</div>
                  <div className="text-xs text-green-600 mt-1">ROI効果: 即座に発現</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};