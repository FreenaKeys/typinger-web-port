# Typinger Web版 - 実装概要

## プロジェクト概要

元のC++デスクトップ版Typingerを、Pythonを用いてWeb化したプロジェクトです。
Flaskをバックエンドとし、JavaScript/HTMLをフロントエンドとして実装しています。

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    ブラウザ（フロントエンド）                  │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   HTML UI    │  │   CSS Style  │  │  JavaScript  │      │
│  │  index.html  │  │  style.css   │  │   main.js    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                                    ↓                │
│         └────────────────  REST API ─────────┘               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│              Flask サーバー（バックエンド）                    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    app.py                            │  │
│  │  （REST APIエンドポイント実装）                        │  │
│  └──────────────────────────────────────────────────────┘  │
│         ↓                                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              core/ コアモジュール                      │  │
│  │                                                       │  │
│  │  • romaji_converter.py      (ローマ字変換)           │  │
│  │  • typing_judge.py          (判定エンジン)           │  │
│  │  • statistics.py            (統計計算)               │  │
│  │  • csv_logger.py            (CSV出力)                │  │
│  │  • scenario_manager.py      (シナリオ管理)           │  │
│  └──────────────────────────────────────────────────────┘  │
│         ↓                                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              ファイルシステム                          │  │
│  │                                                       │  │
│  │  • scenario/        (シナリオJSON)                    │  │
│  │  • output/          (CSV出力)                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## ファイル構成

```
typinger-web/
│
├── app.py                      # Flaskメインアプリケーション
├── config.py                   # 設定ファイル
├── requirements.txt            # Python依存パッケージ
├── setup_scenarios.py          # シナリオセットアップスクリプト
├── run.bat                     # Windows実行スクリプト
├── run.sh                      # Linux/macOS実行スクリプト
│
├── core/                       # コアモジュール
│   ├── __init__.py
│   ├── romaji_converter.py     # ローマ字↔かな変換
│   ├── typing_judge.py         # タイピング判定
│   ├── statistics.py           # 統計計算
│   ├── csv_logger.py           # CSV出力
│   └── scenario_manager.py     # シナリオ管理
│
├── templates/                  # Flaskテンプレート
│   └── index.html             # メインHTML
│
├── static/                     # 静的ファイル
│   ├── css/
│   │   └── style.css          # スタイルシート
│   └── js/
│       └── main.js            # フロントエンドロジック
│
├── tests/                      # テストファイル
│   └── test_core_modules.py   # ユニットテスト
│
├── scenario/                   # シナリオファイル（JSON）
│   ├── beginner.json
│   ├── daily.json
│   └── ...
│
└── output/                     # CSV出力ディレクトリ
```

## コアモジュール詳細

### 1. romaji_converter.py
**機能**: ローマ字とかな文字の相互変換

**主要クラス**:
- `RomajiConverter` - 変換エンジン
- `ConvertStatus` - 変換状態（MATCHED/PARTIAL/NO_MATCH）
- `ConvertResult` - 変換結果

**実装**:
- 変換テーブルベースの実装
- 貪欲マッチ（最長一致）による変換
- 複数のローマ字表記に対応（例: "shi"/"si"）

### 2. typing_judge.py
**機能**: タイピング入力の判定

**主要クラス**:
- `TypingJudge` - 判定エンジン
- `JudgeResult` - 判定結果（CORRECT/INCORRECT/ALREADY_DONE）

**実装**:
- 1文字ずつの逐次判定
- 小文字正規化
- 進捗トラッキング
- 正解率計算

### 3. statistics.py
**機能**: タイピング統計の計算

**主要クラス**:
- `StatisticsCalculator` - 統計計算エンジン
- `KeyEvent` - キーイベント
- `StatisticsData` - 統計データ
- `KanaInputData` - かな別入力時間

**実装**:
- WPM/CPM計算（5文字=1単語）
- キー間隔分析
- かな別入力時間計算
- カテゴリー別頻度計算

### 4. csv_logger.py
**機能**: CSV形式でのデータ出力

**主要クラス**:
- `CSVLogger` - CSV出力

**出力ファイル**:
- `typing_events_YYYYMMDD_HHMMSS.csv` - イベントログ
- `typing_summary_YYYYMMDD_HHMMSS.csv` - 統計サマリ

### 5. scenario_manager.py
**機能**: JSONシナリオファイルの管理

**主要クラス**:
- `ScenarioManager` - シナリオ管理

**機能**:
- ファイル一覧取得
- JSONローディング
- キャッシング機能
- メタデータ取得

## API エンドポイント

### 1. GET `/api/scenarios`
利用可能なシナリオ一覧を取得

**レスポンス**:
```json
{
  "ok": true,
  "scenarios": [
    {
      "title": "初級",
      "filename": "beginner.json",
      "sentence_count": 10
    }
  ]
}
```

### 2. POST `/api/session/start`
タイピングセッションを開始

**リクエスト**:
```json
{
  "scenario_file": "beginner.json"
}
```

**レスポンス**:
```json
{
  "ok": true,
  "session_id": "session_YYYYMMDDHHMMSSSSSSSS",
  "target_text": "ようこそ",
  "target_rubi": "youkoso"
}
```

### 3. GET `/api/session/<session_id>/progress`
現在のセッション進捗を取得

**レスポンス**:
```json
{
  "ok": true,
  "progress": {
    "target_text": "ようこそ",
    "current_position": 2,
    "target_length": 7,
    "progress_percent": 28.5,
    "accuracy": 1.0,
    "correct_count": 2,
    "incorrect_count": 0
  }
}
```

### 4. POST `/api/session/<session_id>/judge_char`
1文字の入力を判定

**リクエスト**:
```json
{
  "char": "y",
  "timestamp": 1234
}
```

**レスポンス**:
```json
{
  "ok": true,
  "result": "correct",
  "progress": { ... }
}
```

### 5. POST `/api/session/<session_id>/backspace`
Backspaceを処理

**リクエスト**:
```json
{
  "timestamp": 1500
}
```

### 6. POST `/api/session/<session_id>/complete`
セッションを完了し統計を計算

**レスポンス**:
```json
{
  "ok": true,
  "statistics": {
    "total_duration_ms": 5234.5,
    "accuracy_percent": 98.5,
    "wpm_correct": 45.2,
    "cpm_correct": 225.0
  },
  "files": {
    "events_csv": "typing_events_20231214_120000.csv",
    "summary_csv": "typing_summary_20231214_120000.csv"
  }
}
```

## フロントエンド（main.js）

**主要クラス**:
- `TypingerApp` - フロントエンドメインロジック

**主要メソッド**:
- `loadScenarios()` - シナリオ一覧の読み込み
- `startSession()` - セッション開始
- `handleKeyDown()` - キー入力処理
- `handleBackspace()` - Backspace処理
- `finishSession()` - セッション完了
- `switchScreen()` - 画面遷移

**状態管理**:
- `sessionId` - 現在のセッションID
- `typingStartTime` - タイピング開始時刻
- `currentScenario` - 現在のシナリオ

## データフロー

### タイピング流れ

```
1. ユーザー: シナリオを選択
   ↓
2. フロントエンド: POST /api/session/start
   ↓
3. バックエンド: TypingJudge, StatisticsCalculator を初期化
   ↓
4. ユーザー: キーを入力
   ↓
5. フロントエンド: POST /api/session/<id>/judge_char
   ↓
6. バックエンド: 
   - RomajiConverter で ローマ字を判定
   - TypingJudge で 正誤判定
   - StatisticsCalculator で 統計記録
   ↓
7. フロントエンド: 画面更新
   ↓
8. ユーザー: 完了まで 4-7 を繰り返す
   ↓
9. フロントエンド: POST /api/session/<id>/complete
   ↓
10. バックエンド:
    - 統計を計算
    - CSVLogger で ファイル出力
    ↓
11. フロントエンド: 統計結果を表示
```

## セッション管理

```python
sessions = {
    "session_YYYYMMDDHHMMSSSSSSSS": {
        'scenario_file': 'beginner.json',
        'target_text': 'テキスト',
        'target_rubi': 'tekisuto',
        'judge': TypingJudge(...),
        'stats_calculator': StatisticsCalculator(...),
        'events': [...],
        'start_time': datetime(...),
    }
}
```

※ 本番環境ではデータベースの使用を推奨

## 拡張可能性

### 追加可能な機能

1. **ユーザー認証**
   - Flask-Login の導入
   - ユーザー管理

2. **スコアボード**
   - データベース（SQLAlchemy）
   - ランキング機能

3. **複数ユーザー対応**
   - セッション永続化
   - プロフィール管理

4. **リアルタイム機能**
   - WebSocket（Flask-SocketIO）
   - マルチプレイタイピング

5. **音声フィードバック**
   - Web Audio API
   - サウンドエフェクト

6. **キーボード分析**
   - ヒートマップ表示
   - キー別パフォーマンス分析

## テスト方法

### ユニットテスト実行
```bash
pytest tests/
```

### 個別テスト実行
```bash
pytest tests/test_core_modules.py -v
```

## 本番環境デプロイ

### Gunicorn での起動
```bash
gunicorn app:app --workers 4 --bind 0.0.0.0:8000
```

### Nginx リバースプロキシ設定
```nginx
server {
    listen 80;
    server_name typinger.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/typinger-web/static;
    }
}
```

## パフォーマンス最適化

1. **フロントエンド**
   - CSS/JS の最小化
   - 画像の最適化
   - キャッシング

2. **バックエンド**
   - シナリオのキャッシング
   - データベース索引（将来）
   - セッションキャッシング

3. **インフラ**
   - CDN配置
   - キャッシュヘッダ設定
   - 圧縮有効化

---

このドキュメントは実装開始時点での設計概要です。
開発進行に応じて更新されます。
