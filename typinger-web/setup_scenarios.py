"""
setup_scenarios.py
シナリオファイルをコピーするスクリプト

元のC++プロジェクトからシナリオファイルをWeb版にコピーします。
"""

import os
import shutil
from pathlib import Path

def setup_scenarios():
    """シナリオファイルをセットアップ"""
    
    # ソースディレクトリ（元のC++プロジェクト）
    source_scenario_dir = Path("../typinger-feature-phase7-kana-intervals/scenario")
    
    # 宛先ディレクトリ
    dest_scenario_dir = Path("scenario")
    
    # 宛先ディレクトリが存在しない場合は作成
    dest_scenario_dir.mkdir(exist_ok=True)
    
    files_copied = 0
    
    if source_scenario_dir.exists() and source_scenario_dir.is_dir():
        # JSONファイルをすべてコピー
        json_files = list(source_scenario_dir.glob("*.json"))
        for json_file in json_files:
            dest_file = dest_scenario_dir / json_file.name
            if not dest_file.exists():
                try:
                    shutil.copy2(json_file, dest_file)
                    print(f"Copied: {json_file.name}")
                    files_copied += 1
                except Exception as e:
                    print(f"Failed to copy {json_file.name}: {e}")
        
        print(f"Total files in scenario directory: {len(list(dest_scenario_dir.glob('*.json')))}")
    else:
        print(f"Source directory not found: {source_scenario_dir}")
        print("Creating sample scenarios instead...")
        
        # サンプルシナリオを作成
        create_sample_scenarios()

def create_sample_scenarios():
    """サンプルシナリオを作成"""
    
    scenario_dir = Path("scenario")
    scenario_dir.mkdir(exist_ok=True)
    
    scenarios = {
        "beginner.json": {
            "title": "初級",
            "entries": {
                "1": {"text": "あいうえお", "rubi": "aiueo"},
                "2": {"text": "かきくけこ", "rubi": "kakikukeko"},
                "3": {"text": "さしすせそ", "rubi": "sashisuseso"},
            }
        },
        "scenarioexample.json": {
            "title": "例題",
            "entries": {
                "1": {"text": "これはダミーです", "rubi": "korehadamidesu"},
                "2": {"text": "こんにちは", "rubi": "konnichiha"},
            }
        },
        "daily.json": {
            "title": "日常会話",
            "entries": {
                "1": {"text": "おはようございます", "rubi": "ohayougozaimasu"},
                "2": {"text": "ありがとうございます", "rubi": "arigatougozaimasu"},
                "3": {"text": "さようなら", "rubi": "sayounara"},
            }
        },
    }
    
    import json
    
    for filename, data in scenarios.items():
        filepath = scenario_dir / filename
        if not filepath.exists():
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Created: {filename}")

if __name__ == "__main__":
    setup_scenarios()
    print("\nScenario setup complete!")
