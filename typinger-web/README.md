# Typinger Web版

**Typinger** は、自作キーボードのテスト用に開発されたオープンソースのタイピング練習ソフトをWeb化したものです。
元のC++デスクトップ版をPython/Flaskを用いてWeb版として移植しました。

## 特徴

### 🎯 タイピング機能
- **日本語ローマ字入力対応**: ひらがな文をローマ字で入力
- **リアルタイム判定**: 正誤判定とフィードバック
- **カスタムシナリオ**: JSON形式でタイピング文を自由に設定

### 📊 統計機能
- **基本統計**: WPM（Words Per Minute）、CPM（Characters Per Minute）、正答率
- **詳細分析**: キー間隔、Backspace回数、かな別入力時間
- **リアルタイム表示**: タイピング完了時に統計情報を画面表示

### 📁 CSV出力機能
- **イベントCSV**: 全キーイベント（KEY_DOWN/KEY_UP/BACKSPACE）をマイクロ秒単位で記録
- **サマリCSV**: セッション全体の統計情報を出力

## 動作環境

- **Python 3.8 以上**
- **Flask 2.3.x**
- **モダンブラウザ** (Chrome, Firefox, Safari, Edge)

## インストール

### 1. リポジトリをクローン
```bash
git clone https://github.com/FreenaKeys/typinger-web.git
cd typinger-web
```

### 2. Python仮想環境を作成（推奨）
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 依存パッケージをインストール
```bash
pip install -r requirements.txt
```

## 使い方

### サーバーを起動
```bash
python app.py
```

ブラウザで `http://localhost:5000` にアクセスしてください。

### 基本的な流れ

1. **シナリオ選択**: 画面から練習用のシナリオファイルを選択
2. **タイピング開始**: 表示されたひらがなをローマ字で入力
3. **統計表示**: タイピング完了後に結果と統計情報を表示

### 操作方法

- **文字入力**: 表示されたひらがなをローマ字で入力
- **Backspace**: 入力ミスを修正
- **完了ボタン**: タイピングを完了
- **中止ボタン**: タイピングを中止

## シナリオファイル

タイピングするテキストは `scenario/` ディレクトリ内のJSONファイルで管理されます。

### シナリオファイルの形式

**形式1: entries形式（推奨）**
```json
{
  "title": "シナリオのタイトル",
  "entries": {
    "1": {
      "text": "これはダミーです",
      "rubi": "korehadamidesu"
    },
    "2": {
      "text": "こんにちは世界",
      "rubi": "konnichihasekaiI"
    }
  }
}
```

**形式2: sentences形式**
```json
{
  "title": "シナリオのタイトル",
  "sentences": [
    "これはダミーです",
    "こんにちは世界",
    "タイピング練習"
  ]
}
```

### カスタムシナリオの作成

`scenario/` ディレクトリに新しいJSONファイルを作成してください。

**例: `scenario/mytext.json`**
```json
{
  "title": "私のシナリオ",
  "entries": {
    "1": {
      "text": "ようこそ",
      "rubi": "youkoso"
    }
  }
}
```

## プロジェクト構成

```
typinger-web/
├── app.py                 # Flaskメインアプリケーション
├── requirements.txt       # Python依存パッケージ
├── README.md             # このファイル
├── core/                 # コアモジュール
│   ├── __init__.py
│   ├── romaji_converter.py    # ローマ字↔かな変換
│   ├── typing_judge.py        # タイピング判定エンジン
│   ├── statistics.py          # 統計計算
│   ├── csv_logger.py          # CSV出力
│   └── scenario_manager.py    # シナリオ管理
├── templates/            # HTMLテンプレート
│   └── index.html        # メイン画面
├── static/               # 静的ファイル
│   ├── css/
│   │   └── style.css     # スタイルシート
│   └── js/
│       └── main.js       # フロントエンドロジック
├── scenario/             # シナリオファイル（JSON）
└── output/               # CSV出力ディレクトリ
```

## API リファレンス

### GET `/api/scenarios`
利用可能なシナリオ一覧を取得

**レスポンス:**
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

### POST `/api/session/start`
タイピングセッションを開始

**リクエスト:**
```json
{
  "scenario_file": "beginner.json"
}
```

**レスポンス:**
```json
{
  "ok": true,
  "session_id": "session_20231214120000000",
  "target_text": "ようこそ",
  "target_rubi": "youkoso"
}
```

### POST `/api/session/<session_id>/judge_char`
1文字の入力を判定

**リクエスト:**
```json
{
  "char": "y",
  "timestamp": 1234
}
```

**レスポンス:**
```json
{
  "ok": true,
  "result": "correct",
  "progress": {
    "target_text": "ようこそ",
    "current_position": 1,
    "accuracy": 1.0,
    "progress_percent": 14.3
  }
}
```

### POST `/api/session/<session_id>/complete`
セッションを完了し統計を計算

**レスポンス:**
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

## 元のプロジェクト

- **元のC++版**: [FreenaKeys/typinger](https://github.com/FreenaKeys/typinger)
- **開発言語**: 元のプロジェクトはC++、このバージョンはPython/Flask

## ライセンス

このプロジェクトは元のTypinger プロジェクトと同じライセンスに従います。
詳細は [LICENSE](LICENSE) を参照してください。

## 貢献

このプロジェクトへの貢献を歓迎します。
大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## トラブルシューティング

### ポート5000が既に使用中の場合
```bash
python app.py # または
# 別のポートを指定
python -c "from app import app; app.run(port=5001)"
```

### シナリオファイルが見つからない
`scenario/` ディレクトリが存在することを確認してください。
存在しない場合はアプリケーションが自動作成します。

### CSVファイルが出力されない
`output/` ディレクトリの権限を確認してください。

## 開発情報

### テスト実行
```bash
pytest tests/
```

### ビルド（本番環境）
```bash
pip install gunicorn
gunicorn app:app
```

---

Typinger Web版 - オープンソース タイピング練習ソフト
