"""
keymap_converter.py
キーマップ形式変換モジュール

JSON ↔ バイナリ形式の相互変換を提供します。
"""

import struct
import base64
from typing import Tuple, Optional, Dict


class KeymapConverter:
    """キーマップ形式変換クラス"""

    MAGIC = 0xA5A5  # マジックナンバー

    @staticmethod
    def json_to_binary(keymap_data: Dict) -> Optional[bytes]:
        """
        JSONキーマップをバイナリに変換
        
        Args:
            keymap_data: キーマップデータ
            
        Returns:
            bytes: バイナリデータ、変換失敗時はNone
        """
        try:
            version = keymap_data.get('version', 1)
            keys = keymap_data.get('keys', [])
            
            # ヘッダーを構築
            header = struct.pack('<H', KeymapConverter.MAGIC)  # MAGIC (2 bytes)
            header += struct.pack('<B', version)              # version (1 byte)
            header += struct.pack('<H', len(keys))            # count (2 bytes)
            
            # ボディを構築
            body = b''
            for key in keys:
                code = key.get('code', 0)
                mods = key.get('mods', 0)
                body += struct.pack('<BB', code, mods)
            
            return header + body
        except Exception:
            return None

    @staticmethod
    def json_to_base64(keymap_data: Dict) -> Optional[str]:
        """
        JSONキーマップをBase64エンコード済みバイナリに変換
        
        Args:
            keymap_data: キーマップデータ
            
        Returns:
            str: Base64エンコード済みバイナリ
        """
        binary = KeymapConverter.json_to_binary(keymap_data)
        if binary is None:
            return None
        
        return base64.b64encode(binary).decode('ascii')

    @staticmethod
    def json_to_hex(keymap_data: Dict) -> Optional[str]:
        """
        JSONキーマップを16進数文字列に変換
        
        Args:
            keymap_data: キーマップデータ
            
        Returns:
            str: 16進数文字列
        """
        binary = KeymapConverter.json_to_binary(keymap_data)
        if binary is None:
            return None
        
        return binary.hex().upper()

    @staticmethod
    def binary_to_json(binary_data: bytes) -> Optional[Dict]:
        """
        バイナリデータをJSONキーマップに変換
        
        Args:
            binary_data: バイナリデータ
            
        Returns:
            Dict: キーマップデータ、変換失敗時はNone
        """
        try:
            if len(binary_data) < 5:  # ヘッダー最小サイズ (2+1+2)
                return None
            
            # ヘッダーを解析
            magic = struct.unpack('<H', binary_data[0:2])[0]
            if magic != KeymapConverter.MAGIC:
                return None
            
            version = struct.unpack('<B', binary_data[2:3])[0]
            count = struct.unpack('<H', binary_data[3:5])[0]
            
            # ボディを解析
            keys = []
            for i in range(count):
                offset = 5 + i * 2
                if offset + 2 > len(binary_data):
                    break
                
                code = struct.unpack('<B', binary_data[offset:offset+1])[0]
                mods = struct.unpack('<B', binary_data[offset+1:offset+2])[0]
                
                keys.append({
                    'code': code,
                    'mods': mods,
                    'label': '',
                })
            
            return {
                'version': version,
                'keys': keys,
            }
        except Exception:
            return None

    @staticmethod
    def base64_to_json(base64_str: str) -> Optional[Dict]:
        """
        Base64文字列をJSONキーマップに変換
        
        Args:
            base64_str: Base64エンコード済みバイナリ
            
        Returns:
            Dict: キーマップデータ
        """
        try:
            binary_data = base64.b64decode(base64_str)
            return KeymapConverter.binary_to_json(binary_data)
        except Exception:
            return None

    @staticmethod
    def hex_to_json(hex_str: str) -> Optional[Dict]:
        """
        16進数文字列をJSONキーマップに変換
        
        Args:
            hex_str: 16進数文字列
            
        Returns:
            Dict: キーマップデータ
        """
        try:
            binary_data = bytes.fromhex(hex_str)
            return KeymapConverter.binary_to_json(binary_data)
        except Exception:
            return None

    @staticmethod
    def get_binary_info(binary_data: bytes) -> Optional[Dict]:
        """
        バイナリデータの情報を取得
        
        Args:
            binary_data: バイナリデータ
            
        Returns:
            Dict: バイナリ情報
        """
        try:
            if len(binary_data) < 5:
                return None
            
            magic = struct.unpack('<H', binary_data[0:2])[0]
            version = struct.unpack('<B', binary_data[2:3])[0]
            count = struct.unpack('<H', binary_data[3:5])[0]
            
            expected_size = 5 + count * 2
            
            return {
                'magic': f"0x{magic:04X}",
                'magic_valid': magic == KeymapConverter.MAGIC,
                'version': version,
                'key_count': count,
                'total_size': len(binary_data),
                'expected_size': expected_size,
                'size_valid': len(binary_data) == expected_size,
            }
        except Exception:
            return None
