"""
keymap_manager.py
カスタムキーマップ管理モジュール

キーマップの検証、管理、変換機能を提供します。
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class KeymapValidator:
    """キーマップ検証クラス"""

    # HID キーコード定義
    HID_KEYS = {
        'A': 4, 'B': 5, 'C': 6, 'D': 7, 'E': 8, 'F': 9, 'G': 10, 'H': 11,
        'I': 12, 'J': 13, 'K': 14, 'L': 15, 'M': 16, 'N': 17, 'O': 18, 'P': 19,
        'Q': 20, 'R': 21, 'S': 22, 'T': 23, 'U': 24, 'V': 25, 'W': 26, 'X': 27,
        'Y': 28, 'Z': 29,
        '1': 30, '2': 31, '3': 32, '4': 33, '5': 34, '6': 35, '7': 36, '8': 37,
        '9': 38, '0': 39,
        'ENTER': 40, 'ESC': 41, 'BACKSPACE': 42, 'TAB': 43, 'SPACE': 44,
        'MINUS': 45, 'EQUALS': 46, 'LEFTBRACE': 47, 'RIGHTBRACE': 48,
        'BACKSLASH': 49, 'SEMICOLON': 51, 'APOSTROPHE': 52, 'GRAVE': 53,
        'COMMA': 54, 'DOT': 55, 'SLASH': 56,
        'UP': 82, 'DOWN': 81, 'LEFT': 80, 'RIGHT': 79,
        'HOME': 74, 'END': 77, 'PAGEUP': 75, 'PAGEDOWN': 78,
        'INSERT': 73, 'DELETE': 76,
        'F1': 58, 'F2': 59, 'F3': 60, 'F4': 61, 'F5': 62, 'F6': 63,
        'F7': 64, 'F8': 65, 'F9': 66, 'F10': 67, 'F11': 68, 'F12': 69,
        'LCTRL': 224, 'LSHIFT': 225, 'LALT': 226, 'LGUI': 227,
        'RCTRL': 228, 'RSHIFT': 229, 'RALT': 230, 'RGUI': 231,
        'NONE': 0,
    }

    # 逆マップ
    CODE_TO_KEY = {v: k for k, v in HID_KEYS.items()}

    @staticmethod
    def validate_json(data: Dict) -> Tuple[bool, List[str]]:
        """
        キーマップJSONを検証
        
        Args:
            data: キーマップデータ
            
        Returns:
            Tuple[bool, List[str]]: (検証結果, エラーリスト)
        """
        errors = []

        # バージョン チェック
        if 'version' not in data:
            errors.append("'version' フィールドが必要です")
        elif not isinstance(data['version'], int) or data['version'] < 0 or data['version'] > 255:
            errors.append("'version' は 0-255 の整数である必要があります")

        # keys チェック
        if 'keys' not in data:
            errors.append("'keys' フィールドが必要です")
        elif not isinstance(data['keys'], list):
            errors.append("'keys' は配列である必要があります")
        else:
            for i, key in enumerate(data['keys']):
                if not isinstance(key, dict):
                    errors.append(f"keys[{i}] はオブジェクトである必要があります")
                    continue

                # code チェック
                if 'code' not in key:
                    errors.append(f"keys[{i}] に 'code' フィールドが必要です")
                elif not isinstance(key['code'], int) or key['code'] < 0 or key['code'] > 255:
                    errors.append(f"keys[{i}].code は 0-255 の整数である必要があります")

                # mods チェック
                if 'mods' not in key:
                    errors.append(f"keys[{i}] に 'mods' フィールドが必要です")
                elif not isinstance(key['mods'], int) or key['mods'] < 0 or key['mods'] > 15:
                    errors.append(f"keys[{i}].mods は 0-15 の整数である必要があります")

        return len(errors) == 0, errors

    @staticmethod
    def get_key_name(code: int) -> str:
        """HID コードからキー名を取得"""
        return KeymapValidator.CODE_TO_KEY.get(code, f"CODE_{code}")

    @staticmethod
    def get_key_code(name: str) -> Optional[int]:
        """キー名からHID コードを取得"""
        return KeymapValidator.HID_KEYS.get(name.upper())


class KeymapManager:
    """キーマップ管理クラス"""

    def __init__(self, keymap_dir: str = "keymaps"):
        """
        コンストラクタ
        
        Args:
            keymap_dir: キーマップファイルのディレクトリ
        """
        self.keymap_dir = keymap_dir
        self._ensure_keymap_dir()

    def _ensure_keymap_dir(self):
        """キーマップディレクトリが存在することを確認"""
        if not os.path.exists(self.keymap_dir):
            os.makedirs(self.keymap_dir)

    def get_keymap_files(self) -> List[Dict[str, str]]:
        """
        キーマップファイル一覧を取得
        
        Returns:
            List[Dict]: ファイル情報のリスト
        """
        files = []
        
        if not os.path.exists(self.keymap_dir):
            return []
        
        for filename in os.listdir(self.keymap_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.keymap_dir, filename)
                files.append({
                    'filename': filename,
                    'filepath': filepath,
                })
        
        return sorted(files, key=lambda x: x['filename'])

    def load_keymap(self, filename: str) -> Optional[Dict]:
        """
        キーマップファイルを読み込む
        
        Args:
            filename: ファイル名
            
        Returns:
            Dict: キーマップデータ
        """
        filepath = os.path.join(self.keymap_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 検証
            is_valid, errors = KeymapValidator.validate_json(data)
            if not is_valid:
                return None
            
            return data
        except Exception:
            return None

    def save_keymap(self, filename: str, data: Dict) -> Tuple[bool, str]:
        """
        キーマップファイルを保存
        
        Args:
            filename: ファイル名
            data: キーマップデータ
            
        Returns:
            Tuple[bool, str]: (成功フラグ, メッセージ)
        """
        # 検証
        is_valid, errors = KeymapValidator.validate_json(data)
        if not is_valid:
            return False, "検証エラー: " + "; ".join(errors)
        
        try:
            filepath = os.path.join(self.keymap_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True, f"ファイル '{filename}' を保存しました"
        except Exception as e:
            return False, f"保存エラー: {str(e)}"

    def delete_keymap(self, filename: str) -> bool:
        """
        キーマップファイルを削除
        
        Args:
            filename: ファイル名
            
        Returns:
            bool: 削除成功の有無
        """
        filepath = os.path.join(self.keymap_dir, filename)
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception:
            pass
        
        return False

    def create_default_keymap(self, key_count: int = 64) -> Dict:
        """
        デフォルトキーマップを作成
        
        Args:
            key_count: キー数
            
        Returns:
            Dict: デフォルトキーマップ
        """
        keys = []
        
        # QWERTY配列の基本キーをマップ
        qwerty_codes = [
            20, 26, 8, 21, 23,  # Q W E R T
            28, 24, 12, 18, 19, # Y U I O P
            4, 22, 7, 9, 10,    # A S D F G
            11, 15, 16, 14, 13, # H J K L semicolon
            29, 27, 3, 2, 30,   # Z X C V B
        ]
        
        for i in range(key_count):
            if i < len(qwerty_codes):
                code = qwerty_codes[i]
                label = KeymapValidator.get_key_name(code)
            else:
                code = 0
                label = f"Key_{i+1}"
            
            keys.append({
                'code': code,
                'mods': 0,
                'label': label,
            })
        
        return {
            'version': 1,
            'keys': keys,
        }

    def validate_keymap(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        キーマップを検証
        
        Args:
            data: キーマップデータ
            
        Returns:
            Tuple[bool, List[str]]: (検証結果, エラーリスト)
        """
        return KeymapValidator.validate_json(data)
