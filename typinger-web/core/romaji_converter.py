"""
romaji_converter.py
ローマ字→かな変換器

用語解説:
- ローマ字(Romaji): キーボードで入力するアルファベット表記（例: "ka", "shi"）
- かな(Kana): 日本語のひらがな（例: "か", "し"）
"""

from enum import Enum
from typing import Dict, Tuple, Optional


class ConvertStatus(Enum):
    MATCHED = "matched"          # 完全一致（変換成功）
    PARTIAL = "partial"          # 部分一致（まだ入力途中）
    NO_MATCH = "no_match"        # 不一致（該当なし）


class ConvertResult:
    def __init__(self, status: ConvertStatus, kana: str = "", 
                 consumed: str = "", remaining: str = ""):
        self.status = status
        self.kana = kana
        self.consumed = consumed
        self.remaining = remaining


class RomajiConverter:
    """ローマ字→かな変換器クラス"""

    def __init__(self):
        self.conversion_table: Dict[str, str] = {}
        self._initialize_table()

    def _initialize_table(self):
        """変換テーブルを初期化"""
        # 基本的なローマ字→かな対応表
        self.conversion_table = {
            # 単独音（あ行）
            'a': 'あ', 'i': 'い', 'u': 'う', 'e': 'え', 'o': 'お',
            
            # か行
            'ka': 'か', 'ki': 'き', 'ku': 'く', 'ke': 'け', 'ko': 'こ',
            
            # さ行
            'sa': 'さ', 'si': 'し', 'su': 'す', 'se': 'せ', 'so': 'そ',
            'sha': 'しゃ', 'shu': 'しゅ', 'sho': 'しょ', 'shi': 'し',
            
            # た行
            'ta': 'た', 'ti': 'ち', 'tu': 'つ', 'te': 'て', 'to': 'と',
            'cha': 'ちゃ', 'chu': 'ちゅ', 'cho': 'ちょ', 'chi': 'ち',
            'tsu': 'つ',
            
            # な行
            'na': 'な', 'ni': 'に', 'nu': 'ぬ', 'ne': 'ね', 'no': 'の',
            
            # は行
            'ha': 'は', 'hi': 'ひ', 'hu': 'ふ', 'he': 'へ', 'ho': 'ほ',
            'fa': 'ふぁ', 'fi': 'ふぃ', 'fe': 'ふぇ', 'fo': 'ふぉ',
            
            # ま行
            'ma': 'ま', 'mi': 'み', 'mu': 'む', 'me': 'め', 'mo': 'も',
            
            # や行
            'ya': 'や', 'yu': 'ゆ', 'yo': 'よ',
            
            # ら行
            'ra': 'ら', 'ri': 'り', 'ru': 'る', 're': 'れ', 'ro': 'ろ',
            
            # わ行
            'wa': 'わ', 'wi': 'ゐ', 'wu': 'う', 'we': 'ゑ', 'wo': 'を', 'n': 'ん',
            
            # ん
            'nn': 'ん', 'n\'': 'ん',
            
            # 濁音（が行）
            'ga': 'が', 'gi': 'ぎ', 'gu': 'ぐ', 'ge': 'げ', 'go': 'ご',
            
            # 濁音（ざ行）
            'za': 'ざ', 'zi': 'じ', 'zu': 'ず', 'ze': 'ぜ', 'zo': 'ぞ',
            'ja': 'じゃ', 'ju': 'じゅ', 'jo': 'じょ',
            
            # 濁音（だ行）
            'da': 'だ', 'di': 'ぢ', 'du': 'づ', 'de': 'で', 'do': 'ど',
            
            # 濁音（ば行）
            'ba': 'ば', 'bi': 'び', 'bu': 'ぶ', 'be': 'べ', 'bo': 'ぼ',
            
            # 半濁音（ぱ行）
            'pa': 'ぱ', 'pi': 'ぴ', 'pu': 'ぷ', 'pe': 'ぺ', 'po': 'ぽ',
            
            # 拗音（きゃ行）
            'kya': 'きゃ', 'kyu': 'きゅ', 'kyo': 'きょ',
            
            # 拗音（しゃ行）
            'sya': 'しゃ', 'syu': 'しゅ', 'syo': 'しょ',
            
            # 拗音（ちゃ行）
            'cya': 'ちゃ', 'cyu': 'ちゅ', 'cyo': 'ちょ',
            
            # 拗音（にゃ行）
            'nya': 'にゃ', 'nyu': 'にゅ', 'nyo': 'にょ',
            
            # 拗音（ひゃ行）
            'hya': 'ひゃ', 'hyu': 'ひゅ', 'hyo': 'ひょ',
            
            # 拗音（みゃ行）
            'mya': 'みゃ', 'myu': 'みゅ', 'myo': 'みょ',
            
            # 拗音（りゃ行）
            'rya': 'りゃ', 'ryu': 'りゅ', 'ryo': 'りょ',
            
            # 拗音（ぎゃ行）
            'gya': 'ぎゃ', 'gyu': 'ぎゅ', 'gyo': 'ぎょ',
            
            # 拗音（じゃ行）
            'jya': 'じゃ', 'jyu': 'じゅ', 'jyo': 'じょ',
            
            # 拗音（びゃ行）
            'bya': 'びゃ', 'byu': 'びゅ', 'byo': 'びょ',
            
            # 拗音（ぴゃ行）
            'pya': 'ぴゃ', 'pyu': 'ぴゅ', 'pyo': 'ぴょ',
        }

    def _has_partial_match(self, romaji: str) -> bool:
        """部分一致チェック（入力途中かどうか）"""
        for key in self.conversion_table:
            if key.startswith(romaji):
                return True
        return False

    def convert(self, input_str: str) -> ConvertResult:
        """ローマ字をかなに変換"""
        input_str = input_str.lower()
        
        # 直接マッチチェック（最長一致）
        for length in range(len(input_str), 0, -1):
            candidate = input_str[:length]
            if candidate in self.conversion_table:
                kana = self.conversion_table[candidate]
                remaining = input_str[length:]
                return ConvertResult(
                    ConvertStatus.MATCHED,
                    kana=kana,
                    consumed=candidate,
                    remaining=remaining
                )
        
        # 部分一致チェック
        if self._has_partial_match(input_str):
            return ConvertResult(ConvertStatus.PARTIAL, remaining=input_str)
        
        return ConvertResult(ConvertStatus.NO_MATCH, remaining=input_str)

    def convert_greedy(self, input_str: str) -> Tuple[str, str]:
        """最長一致変換（貪欲マッチ）"""
        input_str = input_str.lower()
        result_kana = ""
        
        while input_str:
            match_result = self.convert(input_str)
            if match_result.status == ConvertStatus.MATCHED:
                result_kana += match_result.kana
                input_str = match_result.remaining
            else:
                # マッチしない場合はそこで終了
                break
        
        return result_kana, input_str

    def can_convert(self, romaji: str) -> bool:
        """特定のローマ字が変換可能かチェック"""
        return romaji.lower() in self.conversion_table

    def get_table_size(self) -> int:
        """変換テーブルのサイズを取得"""
        return len(self.conversion_table)

    @staticmethod
    def to_romaji(kana: str) -> str:
        """かな→ローマ字変換（逆変換）"""
        kana_to_romaji = {
            'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
            'か': 'ka', 'き': 'ki', 'く': 'ku', 'け': 'ke', 'こ': 'ko',
            'さ': 'sa', 'し': 'shi', 'す': 'su', 'せ': 'se', 'そ': 'so',
            'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
            'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no',
            'は': 'ha', 'ひ': 'hi', 'ふ': 'fu', 'へ': 'he', 'ほ': 'ho',
            'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo',
            'や': 'ya', 'ゆ': 'yu', 'よ': 'yo',
            'ら': 'ra', 'り': 'ri', 'る': 'ru', 'れ': 're', 'ろ': 'ro',
            'わ': 'wa', 'を': 'wo', 'ん': 'n',
            'が': 'ga', 'ぎ': 'gi', 'ぐ': 'gu', 'げ': 'ge', 'ご': 'go',
            'ざ': 'za', 'じ': 'ji', 'ず': 'zu', 'ぜ': 'ze', 'ぞ': 'zo',
            'だ': 'da', 'ぢ': 'di', 'づ': 'du', 'で': 'de', 'ど': 'do',
            'ば': 'ba', 'び': 'bi', 'ぶ': 'bu', 'べ': 'be', 'ぼ': 'bo',
            'ぱ': 'pa', 'ぴ': 'pi', 'ぷ': 'pu', 'ぺ': 'pe', 'ぽ': 'po',
            'きゃ': 'kya', 'きゅ': 'kyu', 'きょ': 'kyo',
            'しゃ': 'sha', 'しゅ': 'shu', 'しょ': 'sho',
            'ちゃ': 'cha', 'ちゅ': 'chu', 'ちょ': 'cho',
            'にゃ': 'nya', 'にゅ': 'nyu', 'にょ': 'nyo',
            'ひゃ': 'hya', 'ひゅ': 'hyu', 'ひょ': 'hyo',
            'みゃ': 'mya', 'みゅ': 'myu', 'みょ': 'myo',
            'りゃ': 'rya', 'りゅ': 'ryu', 'りょ': 'ryo',
            'ぎゃ': 'gya', 'ぎゅ': 'gyu', 'ぎょ': 'gyo',
            'じゃ': 'ja', 'じゅ': 'ju', 'じょ': 'jo',
            'びゃ': 'bya', 'びゅ': 'byu', 'びょ': 'byo',
            'ぴゃ': 'pya', 'ぴゅ': 'pyu', 'ぴょ': 'pyo',
        }
        
        result = ""
        i = 0
        while i < len(kana):
            # 2文字分をチェック
            if i + 1 < len(kana):
                two_char = kana[i:i+2]
                if two_char in kana_to_romaji:
                    result += kana_to_romaji[two_char]
                    i += 2
                    continue
            
            # 1文字分をチェック
            char = kana[i]
            if char in kana_to_romaji:
                result += kana_to_romaji[char]
            else:
                result += char  # 変換できない場合はそのまま
            i += 1
        
        return result
