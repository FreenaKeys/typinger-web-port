"""
scenario_manager.py
シナリオ管理機能

JSONシナリオファイルを読み込み、キャッシング機能を提供します。
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class ScenarioManager:
    """シナリオ管理クラス"""

    def __init__(self, scenario_dir: str = "scenario"):
        """
        コンストラクタ
        
        Args:
            scenario_dir: シナリオファイルが配置されているディレクトリ
        """
        self.scenario_dir = scenario_dir
        self.cache: Dict[str, Dict] = {}  # ファイル名 -> シナリオデータ

    def get_available_scenarios(self) -> List[str]:
        """
        利用可能なシナリオファイルの一覧を取得
        
        Returns:
            List[str]: JSONファイル名のリスト
        """
        if not os.path.exists(self.scenario_dir):
            return []
        
        json_files = []
        for file in os.listdir(self.scenario_dir):
            if file.endswith(".json"):
                json_files.append(file)
        
        return sorted(json_files)

    def load_scenario(self, filename: str) -> Optional[Dict]:
        """
        シナリオファイルを読み込む
        
        Args:
            filename: シナリオファイル名
            
        Returns:
            Dict: シナリオデータ、ファイルが見つからない場合はNone
        """
        # キャッシュをチェック
        if filename in self.cache:
            return self.cache[filename]
        
        filepath = os.path.join(self.scenario_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cache[filename] = data
                return data
        except (json.JSONDecodeError, IOError):
            return None

    def get_random_sentence(self, filename: str) -> Optional[Tuple[str, str]]:
        """
        シナリオからランダムな文を取得
        
        Args:
            filename: シナリオファイル名
            
        Returns:
            Tuple[str, str]: (テキスト, ローマ字) のペア、取得できない場合はNone
        """
        scenario = self.load_scenario(filename)
        
        if not scenario:
            return None
        
        # "entries"または"sentences"キーをチェック
        if "entries" in scenario and isinstance(scenario["entries"], dict):
            # entries形式（キーペアが各エントリに含まれている）
            import random
            entries = scenario["entries"]
            if not entries:
                return None
            
            key = random.choice(list(entries.keys()))
            entry = entries[key]
            
            if "text" in entry and "rubi" in entry:
                return (entry["text"], entry["rubi"])
        
        elif "sentences" in scenario and isinstance(scenario["sentences"], list):
            # sentences形式（テキストのみ、ローマ字は自動生成の場合）
            import random
            sentences = scenario["sentences"]
            if not sentences:
                return None
            
            text = random.choice(sentences)
            return (text, text)  # ローマ字は別途変換が必要
        
        return None

    def get_first_sentence(self, filename: str) -> Optional[Tuple[str, str]]:
        """
        シナリオから最初の文を取得
        
        Args:
            filename: シナリオファイル名
            
        Returns:
            Tuple[str, str]: (テキスト, ローマ字) のペア、取得できない場合はNone
        """
        scenario = self.load_scenario(filename)
        
        if not scenario:
            return None
        
        # "entries"形式
        if "entries" in scenario and isinstance(scenario["entries"], dict):
            entries = scenario["entries"]
            if "1" in entries:
                entry = entries["1"]
                if "text" in entry and "rubi" in entry:
                    return (entry["text"], entry["rubi"])
        
        # "sentences"形式
        elif "sentences" in scenario and isinstance(scenario["sentences"], list):
            sentences = scenario["sentences"]
            if sentences:
                text = sentences[0]
                return (text, text)
        
        return None

    def get_all_sentences(self, filename: str) -> List[Tuple[str, str]]:
        """
        シナリオからすべての文を取得
        
        Args:
            filename: シナリオファイル名
            
        Returns:
            List[Tuple[str, str]]: [(テキスト, ローマ字)] のリスト
        """
        scenario = self.load_scenario(filename)
        
        if not scenario:
            return []
        
        sentences = []
        
        # "entries"形式
        if "entries" in scenario and isinstance(scenario["entries"], dict):
            entries = scenario["entries"]
            for key in sorted(entries.keys()):
                entry = entries[key]
                if "text" in entry and "rubi" in entry:
                    sentences.append((entry["text"], entry["rubi"]))
        
        # "sentences"形式
        elif "sentences" in scenario and isinstance(scenario["sentences"], list):
            for text in scenario["sentences"]:
                sentences.append((text, text))
        
        return sentences

    def get_scenario_info(self, filename: str) -> Optional[Dict]:
        """
        シナリオの情報を取得
        
        Args:
            filename: シナリオファイル名
            
        Returns:
            Dict: シナリオ情報（タイトル、文数など）
        """
        scenario = self.load_scenario(filename)
        
        if not scenario:
            return None
        
        info = {
            "title": scenario.get("title", filename),
            "filename": filename,
        }
        
        # 文数をカウント
        if "entries" in scenario:
            info["sentence_count"] = len(scenario["entries"])
        elif "sentences" in scenario:
            info["sentence_count"] = len(scenario["sentences"])
        
        return info

    def clear_cache(self):
        """キャッシュをクリア"""
        self.cache.clear()
