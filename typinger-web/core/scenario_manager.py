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

    def validate_scenario(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        シナリオJSONを検証
        
        Args:
            data: シナリオデータ
            
        Returns:
            Tuple[bool, List[str]]: (検証結果, エラーリスト)
        """
        errors = []

        # メタデータチェック
        if 'meta' not in data:
            errors.append("'meta' フィールドが必要です")
        else:
            meta = data['meta']
            
            if 'name' not in meta:
                errors.append("'meta.name' が必要です")
            elif not isinstance(meta['name'], str) or len(meta['name']) == 0:
                errors.append("'meta.name' は空でない文字列である必要があります")
            
            if 'uniqueid' not in meta:
                errors.append("'meta.uniqueid' が必要です")
            elif not isinstance(meta['uniqueid'], str):
                errors.append("'meta.uniqueid' は文字列である必要があります")

        # エントリチェック
        if 'entries' not in data and 'sentences' not in data:
            errors.append("'entries' または 'sentences' フィールドが必要です")
        else:
            entries = data.get('entries', data.get('sentences', {}))
            
            if not isinstance(entries, dict):
                errors.append("'entries' はオブジェクトである必要があります")
            elif len(entries) == 0:
                errors.append("'entries' は少なくとも1つのエントリが必要です")
            else:
                for key, entry in entries.items():
                    if not isinstance(entry, dict):
                        errors.append(f"entries[{key}] はオブジェクトである必要があります")
                        continue
                    
                    if 'text' not in entry:
                        errors.append(f"entries[{key}] に 'text' フィールドが必要です")
                    
                    if 'rubi' not in entry:
                        errors.append(f"entries[{key}] に 'rubi' フィールドが必要です")

        return len(errors) == 0, errors

    def save_scenario(self, filename: str, data: Dict) -> Tuple[bool, str]:
        """
        シナリオを保存
        
        Args:
            filename: シナリオファイル名
            data: シナリオデータ
            
        Returns:
            Tuple[bool, str]: (成功/失敗, メッセージ)
        """
        try:
            # バリデーション
            valid, errors = self.validate_scenario(data)
            if not valid:
                return False, f"バリデーションエラー: {', '.join(errors[:3])}"
            
            # ファイル名サニタイズ
            filename = filename.replace('..', '').replace('/', '').replace('\\', '')
            if not filename.endswith('.json'):
                filename += '.json'
            
            # ディレクトリ作成
            os.makedirs(self.scenario_dir, exist_ok=True)
            
            filepath = os.path.join(self.scenario_dir, filename)
            
            # セキュリティチェック
            if not os.path.abspath(filepath).startswith(os.path.abspath(self.scenario_dir)):
                return False, "無効なパス"
            
            # ファイル書き込み
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # キャッシュクリア
            self.clear_cache()
            
            return True, f"シナリオを保存しました: {filename}"
        except Exception as e:
            return False, f"保存エラー: {str(e)}"

    def delete_scenario(self, filename: str) -> Tuple[bool, str]:
        """
        シナリオを削除
        
        Args:
            filename: シナリオファイル名
            
        Returns:
            Tuple[bool, str]: (成功/失敗, メッセージ)
        """
        try:
            # ファイル名サニタイズ
            filename = filename.replace('..', '').replace('/', '').replace('\\', '')
            if not filename.endswith('.json'):
                filename += '.json'
            
            filepath = os.path.join(self.scenario_dir, filename)
            
            # セキュリティチェック
            if not os.path.abspath(filepath).startswith(os.path.abspath(self.scenario_dir)):
                return False, "無効なパス"
            
            if not os.path.exists(filepath):
                return False, "シナリオが見つかりません"
            
            os.remove(filepath)
            
            # キャッシュクリア
            self.clear_cache()
            
            return True, f"シナリオを削除しました: {filename}"
        except Exception as e:
            return False, f"削除エラー: {str(e)}"

    def create_default_scenario(self) -> Dict:
        """
        デフォルトシナリオテンプレートを作成
        
        Returns:
            Dict: シナリオテンプレート
        """
        from datetime import datetime
        
        return {
            "meta": {
                "name": "新しいシナリオ",
                "uniqueid": f"com.typinger.custom_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "requiredver": "0.1.0"
            },
            "entries": {
                "1": {
                    "text": "テキスト",
                    "rubi": "tekisuto",
                    "level": "beginner"
                }
            }
        }

