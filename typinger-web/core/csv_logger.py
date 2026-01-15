"""
csv_logger.py
CSV出力機能

タイピング結果をCSV形式で保存する機能を提供します。
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Any
from core.statistics import KeyEvent, EventType, StatisticsData


class CSVLogger:
    """CSV出力クラス"""

    def __init__(self, output_dir: str = "output"):
        """
        コンストラクタ
        
        Args:
            output_dir: 出力ディレクトリ
        """
        self.output_dir = output_dir
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """出力ディレクトリが存在することを確認"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _get_timestamp_filename(self, prefix: str, ext: str = "csv") -> str:
        """タイムスタンプ付きファイル名を生成"""
        now = datetime.now()
        filename = f"{prefix}_{now.strftime('%Y%m%d_%H%M%S')}.{ext}"
        return os.path.join(self.output_dir, filename)

    def save_events_csv(self, events: List[KeyEvent]) -> str:
        """
        イベントCSVを保存
        
        全キーイベント（KEY_DOWN/KEY_UP/BACKSPACE）をマイクロ秒単位で記録
        
        Args:
            events: キーイベントのリスト
            
        Returns:
            str: 保存されたファイルパス
        """
        filepath = self._get_timestamp_filename("typing_events")
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp (microseconds)", "event_type", "virtual_key", "character"])
            
            for event in events:
                writer.writerow([
                    event.timestamp,
                    event.event_type.value,
                    event.virtual_key,
                    event.character,
                ])
        
        return filepath

    def save_summary_csv(self, stats_data: StatisticsData, 
                         target_text: str, accuracy: float) -> str:
        """
        サマリCSVを保存
        
        セッション全体の統計情報を出力
        
        Args:
            stats_data: 統計データ
            target_text: 目標テキスト
            accuracy: 正解率
            
        Returns:
            str: 保存されたファイルパス
        """
        filepath = self._get_timestamp_filename("typing_summary")
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # ヘッダーとデータ
            summary_data = [
                ["Metric", "Value"],
                ["Target Text", target_text],
                ["Total Duration (microseconds)", stats_data.total_duration],
                ["Total Duration (seconds)", stats_data.total_duration / 1000000],
                ["Total Key Count", stats_data.total_key_count],
                ["Correct Key Count", stats_data.correct_key_count],
                ["Incorrect Key Count", stats_data.incorrect_key_count],
                ["Backspace Count", stats_data.backspace_count],
                ["Accuracy (%)", f"{accuracy * 100:.2f}"],
                ["WPM (Total)", f"{stats_data.wpm_total:.2f}"],
                ["WPM (Correct)", f"{stats_data.wpm_correct:.2f}"],
                ["CPM (Total)", f"{stats_data.cpm_total:.2f}"],
                ["CPM (Correct)", f"{stats_data.cpm_correct:.2f}"],
                ["Avg Inter-Key Interval (ms)", f"{stats_data.avg_inter_key_interval:.2f}"],
                ["Min Inter-Key Interval (ms)", f"{stats_data.min_inter_key_interval:.2f}"],
                ["Max Inter-Key Interval (ms)", f"{stats_data.max_inter_key_interval:.2f}"],
            ]
            
            writer.writerows(summary_data)
        
        return filepath

    def save_kana_analysis_csv(self, kana_analysis: Dict[str, Any]) -> str:
        """
        かな別分析CSVを保存
        
        各かなの平均入力時間を記録
        
        Args:
            kana_analysis: かな別分析データ
            
        Returns:
            str: 保存されたファイルパス
        """
        filepath = self._get_timestamp_filename("kana_analysis")
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Kana", "Avg Input Time (ms)", "Count"])
            
            for kana, data in kana_analysis.items():
                writer.writerow([
                    kana,
                    f"{data.get('avg_time', 0):.2f}",
                    data.get('count', 0),
                ])
        
        return filepath
