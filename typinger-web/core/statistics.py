"""
statistics.py
タイピング統計計算モジュール

用語解説:
- WPM (Words Per Minute): 1分あたりの入力単語数（英語では5文字=1単語）
- CPM (Characters Per Minute): 1分あたりの入力文字数
- キー間隔 (Inter-Key Interval): 連続するキー入力間の時間差
"""

from enum import Enum
from typing import Dict, List
from dataclasses import dataclass, field
import statistics as stats


class EventType(Enum):
    KEY_DOWN = "key_down"
    KEY_UP = "key_up"
    BACKSPACE = "backspace"


@dataclass
class KeyEvent:
    """キーイベント情報"""
    event_type: EventType
    timestamp: int  # マイクロ秒単位
    virtual_key: int  # 仮想キーコード
    character: str  # 実際の文字（ASCII）


@dataclass
class KanaInputData:
    """かな入力データ"""
    kana: str  # 仮名文字（例: "し", "しゅ"）
    romaji: str  # 対応するローマ字（例: "shi", "shu"）
    start_time: int  # 先頭キーダウン（マイクロ秒）
    end_time: int  # 最後のキーアップ（マイクロ秒）
    
    @property
    def duration(self) -> int:
        """所要時間（マイクロ秒）"""
        return self.end_time - self.start_time


@dataclass
class StatisticsData:
    """統計データ"""
    # 基本情報
    total_duration: int = 0  # 総時間（マイクロ秒）
    total_key_count: int = 0  # 総キー入力数（Backspace含む）
    correct_key_count: int = 0  # 正解キー数
    incorrect_key_count: int = 0  # 誤入力キー数
    backspace_count: int = 0  # Backspace回数
    
    # WPM/CPM
    wpm_total: float = 0.0  # 総入力ベースWPM
    wpm_correct: float = 0.0  # 正答ベースWPM
    cpm_total: float = 0.0  # 総入力ベースCPM
    cpm_correct: float = 0.0  # 正答ベースCPM
    
    # キー間隔
    avg_inter_key_interval: float = 0.0  # 平均キー間隔（ミリ秒）
    min_inter_key_interval: float = 0.0  # 最小キー間隔（ミリ秒）
    max_inter_key_interval: float = 0.0  # 最大キー間隔（ミリ秒）
    
    # キー別平均時間
    avg_key_press_duration: Dict[str, float] = field(default_factory=dict)
    
    # 50音別入力時間
    kana_input_time: Dict[str, float] = field(default_factory=dict)


class StatisticsCalculator:
    """統計計算クラス"""
    
    # 重要かな文字リスト（30文字）
    IMPORTANT_KANA = [
        # K行（5文字）
        "か", "き", "く", "け", "こ",
        # N行+ん（6文字）
        "な", "に", "ぬ", "ね", "の", "ん",
        # 母音（5文字）
        "あ", "い", "う", "え", "お",
        # 高頻度子音（7文字）
        "し", "た", "と", "て", "さ", "す", "は",
        # 拗音（7文字）
        "しゃ", "しゅ", "しょ", "きゃ", "きゅ", "ちゃ", "ちゅ",
    ]
    
    # かなカテゴリー定義
    KANA_CATEGORIES = {
        "母音": ["あ", "い", "う", "え", "お"],
        "K行": ["か", "き", "く", "け", "こ"],
        "S行": ["さ", "し", "す", "せ", "そ"],
        "T行": ["た", "ち", "つ", "て", "と"],
        "N行": ["な", "に", "ぬ", "ね", "の"],
        "H行": ["は", "ひ", "ふ", "へ", "ほ"],
        "M行": ["ま", "み", "む", "め", "も"],
        "Y行": ["や", "ゆ", "よ"],
        "R行": ["ら", "り", "る", "れ", "ろ"],
        "W行": ["わ", "を", "ん"],
    }

    def __init__(self):
        self.events: List[KeyEvent] = []
        self.session_start_time: int = 0
        self.kana_input_data: List[KanaInputData] = []

    def add_event(self, event: KeyEvent):
        """イベントを追加"""
        if not self.events:
            self.session_start_time = event.timestamp
        self.events.append(event)

    def calculate_statistics(self, correct_key_count: int, 
                           target_text_length: int) -> StatisticsData:
        """統計を計算"""
        if not self.events:
            return StatisticsData()
        
        stats_data = StatisticsData()
        
        # 基本情報
        stats_data.total_duration = self.events[-1].timestamp - self.session_start_time
        stats_data.total_key_count = len(self.events)
        stats_data.correct_key_count = correct_key_count
        stats_data.incorrect_key_count = stats_data.total_key_count - correct_key_count
        stats_data.backspace_count = sum(1 for e in self.events if e.event_type == EventType.BACKSPACE)
        
        # WPM/CPM計算（5文字=1単語）
        if stats_data.total_duration > 0:
            minutes = stats_data.total_duration / (1000000 * 60)
            if minutes > 0:
                stats_data.wpm_total = (stats_data.total_key_count / 5) / minutes
                stats_data.wpm_correct = (stats_data.correct_key_count / 5) / minutes
                stats_data.cpm_total = stats_data.total_key_count / minutes
                stats_data.cpm_correct = stats_data.correct_key_count / minutes
        
        # キー間隔計算
        inter_key_intervals = []
        for i in range(1, len(self.events)):
            interval = self.events[i].timestamp - self.events[i-1].timestamp
            inter_key_intervals.append(interval)
        
        if inter_key_intervals:
            stats_data.avg_inter_key_interval = sum(inter_key_intervals) / len(inter_key_intervals) / 1000  # ミリ秒
            stats_data.min_inter_key_interval = min(inter_key_intervals) / 1000
            stats_data.max_inter_key_interval = max(inter_key_intervals) / 1000
        
        return stats_data

    def get_top_n_kana_by_time(self, kana_input_data: List[KanaInputData], n: int = 5) -> List[tuple]:
        """かな入力時間のトップNを取得"""
        if not kana_input_data:
            return []
        
        # かな別の平均入力時間を計算
        kana_times: Dict[str, List[int]] = {}
        for data in kana_input_data:
            if data.kana not in kana_times:
                kana_times[data.kana] = []
            kana_times[data.kana].append(data.duration)
        
        # 平均を計算
        avg_times = [
            (kana, sum(times) / len(times) / 1000)  # ミリ秒
            for kana, times in kana_times.items()
        ]
        
        # 時間でソート（降順）
        avg_times.sort(key=lambda x: x[1], reverse=True)
        
        return avg_times[:n]

    def get_category_frequency(self, target_text: str) -> Dict[str, int]:
        """カテゴリー別出現頻度を計算"""
        frequency = {cat: 0 for cat in self.KANA_CATEGORIES}
        
        for char in target_text:
            for category, kanas in self.KANA_CATEGORIES.items():
                if char in kanas:
                    frequency[category] += 1
        
        return frequency

    def get_important_kana_frequency(self, target_text: str) -> Dict[str, int]:
        """重要かな30文字の出現頻度を計算"""
        frequency = {kana: 0 for kana in self.IMPORTANT_KANA}
        
        for char in target_text:
            if char in frequency:
                frequency[char] += 1
        
        return {k: v for k, v in frequency.items() if v > 0}
