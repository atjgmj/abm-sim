# CLAUDE.md — ABMコミュニケーション施策シミュレータ（デモ）実装要件

この文書は、**3rd Party登録・課金なし**で動くデモ実装を対象に、AIコラボレータ（Claude等）が開発補助を行うための作業仕様を定義する。

---

## 1. 目的 / 成果物

* **目的**: ABMでコミュニケーション施策の効果をシミュレーションする“触れるデモ”をローカル実行で提供。
* **成果物**

  * 最小MVPアプリ（フロント/バックエンド/ABMモデル）
  * ネットワーク拡散アニメーション + KPI（認知/興味/理解/好意/利用意向）の時系列・比較
  * シナリオA/Bの差分ハイライト
  * CSV/JSONエクスポート
  * README（起動手順）

---

## 2. 非機能・制約

* **禁止**: 有料/登録必須の第三者サービス、SaaSキー、クラウド課金。
* **実行環境**: ローカルPC（Docker任意）。
* **データ**: デモでは合成データのみ。PIIは扱わない。
* **性能目安**: 1万エージェント×60日×反復10を実行完了（数分〜十数分目安）。
* **可搬性**: Mac/Win/Linux で再現可能。

---

## 3. 技術スタック（OSSのみ）

* フロント: **React + TypeScript + Vite + Tailwind**、可視化: **Recharts**（時系列）, **vis-network or D3**（グラフ）
* バックエンド: **FastAPI (Python)**
* モデル: **Mesa + NetworkX + NumPy**
* ストレージ: **SQLite**（メタ）+ **Parquet**（結果）/ 代替としてJSON/CSV
* パッケージ管理: **uv or poetry**（Python）, **pnpm**（Node）

---

## 4. ユースケース / 画面

1. **シナリオ作成**: KPIカテゴリ/粒度、媒体配分、口コミ率、ステップ数、反復回数、乱数シードを設定。
2. **ネットワーク生成**: ランダム/スモールワールド/スケールフリーの選択とプレビュー。
3. **実行**: 進行率を表示し、完了後に結果取得。
4. **結果閲覧**: KPI時系列、ネットワーク拡散アニメ、A/B比較、差分表。
5. **保存/共有**: シナリオと結果をJSON/CSVで出力。

---

## 5. モデル要件（ABM）

* **状態**: 未認知→認知→興味→理解→好意→意向→採用（可変ファネル、遷移確率は媒体/口コミ/忘却の影響を受ける）。
* **エージェント属性**: 興味度・受容性・影響力（分布で初期化）。
* **ネットワーク**: Nノード、平均次数k、生成器（ER/WS/BA）。辺は無向、重みは接触頻度近似（初期は1）。
* **介入**: 媒体別到達×頻度×効果α。口コミは採用/高好意ノードから隣接へ確率伝播、時間減衰あり。
* **計測**: KPIカテゴリ別人数、CV、CPA/ROAS（媒体コストから算出）。

---

## 6. KPI設定

* カテゴリ候補: **認知 / 興味 / 理解 / 好意 / 利用意向**
* 粒度選択: **ブランド / サービス / 施策**
* UIでは目的関数（例: 利用意向最大、CPA最小、加重ROAS最大）を選択可能。

---

## 7. APIコントラクト（MVP）

* `POST /api/scenario` → {id}
* `POST /api/run` → {run\_id}
* `GET /api/run/{id}/status` → {status: queued|running|done|error, progress:\[0..1]}
* `GET /api/run/{id}/results?agg=day` → 時系列データ（例下記）
* `POST /api/network/preview` → {nodes:\[...], edges:\[...]}

### 7.1 サンプル: リクエスト/レスポンス

**Scenario（POST）**

```json
{
  "name": "Baseline A",
  "kpi": {"categories": ["awareness","interest","knowledge","liking","intent"], "granularity": "brand"},
  "media_mix": {"sns": {"share": 0.5, "alpha": 0.03}, "video": {"share": 0.3, "alpha": 0.02}, "search": {"share": 0.2, "alpha": 0.01}},
  "wom": {"p_generate": 0.08, "decay": 0.9},
  "network": {"type": "ws", "n": 10000, "k": 6, "beta": 0.1},
  "steps": 60, "reps": 10, "seed": 42
}
```

**Results（GET）**

```json
{
  "run_id": "r-123",
  "series": [
    {"day": 0, "metric": "awareness", "value": 120},
    {"day": 1, "metric": "awareness", "value": 340},
    {"day": 1, "metric": "intent", "value": 25}
  ],
  "summary": {"awareness": {"start": 120, "end": 5800, "delta": 5680}}
}
```

---

## 8. JSON Schema（抜粋）

**Scenario**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["kpi","media_mix","wom","network","steps"],
  "properties": {
    "name": {"type": "string"},
    "kpi": {
      "type": "object",
      "properties": {
        "categories": {"type": "array", "items": {"enum": ["awareness","interest","knowledge","liking","intent"]}},
        "granularity": {"enum": ["brand","service","campaign"]}
      },
      "required": ["categories","granularity"]
    },
    "media_mix": {"type": "object"},
    "wom": {"type": "object", "properties": {"p_generate": {"type":"number"}, "decay": {"type":"number"}}},
    "network": {"type": "object", "properties": {"type":{"enum":["er","ws","ba"]}, "n":{"type":"integer"}, "k":{"type":"integer"}, "beta":{"type":"number"}}},
    "steps": {"type": "integer"},
    "reps": {"type": "integer"},
    "seed": {"type": "integer"}
  }
}
```

---

## 9. UI要件（主要コンポーネント）

* **ScenarioForm**: JSON Schema駆動（説明、単位、範囲、依存関係）。
* **NetworkPreview**: n,k,β変更で即時再描画。ノード1k/辺5kまで滑らかに。
* **RunPanel**: 進行率表示、キャンセル、乱数シード固定。
* **Dashboard**: 複数シリーズ重ね描画、A/B比較タブ、差分表。
* **Export**: CSV/JSONダウンロード。

---

## 10. 既定値（デモ）

* N=10,000、k=6、WS β=0.1
* 媒体: SNS 50% α=0.03、動画30% α=0.02、検索20% α=0.01
* 口コミ: p=0.08、decay=0.9、忘却=0.01/step
* 60日、反復10、seed=42

---

## 11. 受け入れ基準（Acceptance Criteria）

* [ ] ローカルで `pnpm dev` + `uv run` で起動し、ブラウザから操作可能
* [ ] 1万ノード・60日・反復10で完走し、KPI時系列が描画される
* [ ] ネットワーク拡散アニメが視覚的に確認できる
* [ ] シナリオA/Bを保存し、差分チャートと差分表が表示される
* [ ] 結果と設定をCSV/JSONでエクスポートできる

---

## 12. リポジトリ構成

```
repo/
  backend/
    app.py
    model/
      abm.py
      network.py
      metrics.py
    store/
      db.py
      io.py
    schemas.py
  frontend/
    src/
      pages/
      components/
      api/
      charts/
  docker-compose.yml
  README.md
```

---

## 13. 開発ガイドライン

* コーディング: 型注釈（Python/TS）、ESLint + Ruff推奨、関数は純粋性を優先。
* テスト: 最低限のユニットテスト（遷移・集計・API契約）。
* 再現性: 乱数シード固定、バージョンピン止め（lockfile）。
* ドキュメント: READMEに起動/操作/制限を明示。スクリーンショット1枚以上。

---

## 14. 将来拡張のフック（スコープ外だが設計で準備）

* データ接続（CSV/DB）
* 感度分析（パラメータ掃引）/ 最適化（メディア配分探索）
* RBAC/SSO、監査ログ、設定バージョン管理

---

## 15. 用語（対訳）

* awareness=認知, interest=興味, knowledge=理解, liking=好意, intent=利用意向
* ER=Erdős–Rényi, WS=Watts–Strogatz, BA=Barabási–Albert
