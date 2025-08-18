// パラメータの日本語説明
export const PARAMETER_TOOLTIPS = {
  // Media Mix
  mediaShare: "メディア全体の予算における各チャネルの配分比率\n0.0-1.0の間で設定し、合計が1.0になるように自動調整されます",
  snsShare: "SNS（Twitter、Instagram等）の予算配分\n若年層・都市部でのリーチが高い傾向",
  videoShare: "動画メディア（YouTube、TikTok等）の予算配分\n視覚的インパクトが高く、エンゲージメント率が高い",
  searchShare: "検索連動広告の予算配分\n購買意向の高いユーザーにリーチ可能",
  
  mediaAlpha: "メディアの効果係数（影響の強さ）\n値が高いほど同じ予算でもより多くの人に影響を与える",
  snsAlpha: "SNSの効果係数\n一般的に0.01-0.05程度。バイラル効果も期待できる",
  videoAlpha: "動画メディアの効果係数\n視覚的訴求力が高いため、やや高めに設定",
  searchAlpha: "検索広告の効果係数\n購買意向が高いユーザーのため効果は高い",

  // Word of Mouth
  womGenerate: "口コミ発生確率\n満足したユーザーが他の人に情報を伝える確率\n0.02-0.2程度が現実的",
  womDecay: "記憶減衰率\n時間経過による記憶の薄れやすさ\n1.0に近いほど記憶が持続する",
  personalityWeight: "個性による口コミ影響度\n個人の性格特性が口コミ効果に与える影響の重み",
  demographicWeight: "人口統計による口コミ影響度\n年齢・所得等の属性が口コミ効果に与える影響の重み",

  // Network Configuration
  networkType: "ネットワーク構造の種類\n• Erdős-Rényi: ランダムネットワーク\n• Watts-Strogatz: スモールワールド（現実的）\n• Barabási-Albert: スケールフリー",
  networkNodes: "シミュレーション対象者数\n多いほど詳細だが計算時間も増加\n1万人程度が標準的",
  avgDegree: "1人あたりの平均人脈数\n現実では6-8人程度が一般的\nSNS時代はより多い場合も",
  rewiringProb: "結び直し確率（Watts-Strogatzのみ）\n0.1程度で現実的なスモールワールド構造",

  // Personality Configuration
  openness: "新しいもの好き度（開放性）\n新製品・新サービスへの受容度\n高いほどイノベーター的",
  socialInfluence: "社会的影響受容度\n他人の意見や行動に影響されやすさ\n高いほど流行に敏感",
  mediaAffinity: "メディア接触度\n各種メディアとの親和性の高さ\n高いほど広告を見る機会が多い",
  riskTolerance: "リスク許容度\n新しいことへの挑戦意欲\n高いほど早期採用者になりやすい",

  // Demographics Configuration
  ageGroup: "年齢層の設定\n1: 18-24歳、2: 25-34歳、3: 35-44歳\n4: 45-54歳、5: 55歳以上\n若いほどデジタルメディアに親和的",
  incomeLevel: "所得レベル\n1: 低所得、3: 中所得、5: 高所得\n購買力と情報収集能力に影響",
  urbanRural: "都市度\n0.0: 完全に地方、1.0: 完全に都市部\n都市部ほどメディア接触機会が多い",
  educationLevel: "教育レベル\n1: 中学、2: 高校、3: 大学、4: 学士、5: 大学院\n情報処理能力と批判的思考力に影響",

  // Influencer Configuration
  enableInfluencers: "インフルエンサーの存在\nオンにすると特別な影響力を持つ人が含まれる\n現代のマーケティングでは重要な要素",
  influencerRatio: "インフルエンサーの比率\n全体に対するインフルエンサーの割合\n現実的には1-3%程度",
  influenceMultiplier: "インフルエンサーの影響倍率\n一般的な人の何倍の影響力を持つか\n3-5倍程度が現実的",

  // Simulation Parameters
  steps: "シミュレーション日数\n何日間の効果を見るか\n通常のキャンペーンは30-90日程度",
  repetitions: "試行回数\n同じ条件で何回実行するか\n多いほど結果の信頼性が高まる（10回程度が標準）",
  randomSeed: "乱数シード\n結果の再現性を保つための値\n同じ値なら常に同じ結果になる",

  // KPI Configuration
  awareness: "認知率\n商品・サービスを知っている人の割合\nマーケティングの最初の目標",
  interest: "関心度\n認知した人のうち関心を示した人の割合\n購買ファネルの第2段階",
  knowledge: "理解度\n詳しく内容を理解している人の割合\n比較検討段階に相当",
  liking: "好意度\n商品・サービスに好意的な印象を持つ人の割合\n ブランド形成の指標",
  intent: "購買意向\n実際に購入を検討している人の割合\n最終的な成果指標",
  
  // Calibration
  trendingTopics: "現在注目されているキーワード\nクリックすると自動的にキャンペーンキーワードに追加されます",
  campaignKeywords: "キャンペーンのキーワード\nカンマ区切りで複数指定可能\n実際のソーシャルメディアデータから設定を最適化",
  trainingData: "機械学習の訓練データ\n過去のシミュレーション結果から最適なパラメータを学習\n20回以上の実行で精度が向上",
  confidence: "結果の信頼度\n予測や最適化結果の確からしさ\n70%以上で高信頼、40%未満で要注意"
};