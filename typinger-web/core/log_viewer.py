"""
log_viewer.py
ログビューア・管理画面用モジュール

CSVファイルの管理、表示、分析機能を提供します。
"""

import os
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class LogViewer:
    """ログビューアクラス"""

    def __init__(self, output_dir: str = "output"):
        """
        コンストラクタ
        
        Args:
            output_dir: ログファイルの出力ディレクトリ
        """
        self.output_dir = output_dir
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """出力ディレクトリが存在することを確認"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def get_csv_files(self) -> List[Dict[str, Any]]:
        """
        CSVファイルの一覧を取得
        
        Returns:
            List[Dict]: ファイル情報のリスト
        """
        csv_files = []
        
        if not os.path.exists(self.output_dir):
            return []
        
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(self.output_dir, filename)
                stat = os.stat(filepath)
                
                csv_files.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': stat.st_size,
                    'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'file_type': self._determine_file_type(filename),
                })
        
        # 更新日時でソート（新しい順）
        csv_files.sort(key=lambda x: x['modified_time'], reverse=True)
        
        return csv_files

    def _determine_file_type(self, filename: str) -> str:
        """ファイルタイプを判定"""
        if 'events' in filename:
            return 'events'
        elif 'summary' in filename:
            return 'summary'
        elif 'kana_analysis' in filename:
            return 'kana_analysis'
        else:
            return 'unknown'

    def read_csv_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        CSVファイルを読み込み
        
        Args:
            filename: ファイル名
            
        Returns:
            Dict: CSVデータ（ヘッダー + 行データ）
        """
        filepath = os.path.join(self.output_dir, filename)
        
        # セキュリティチェック：ディレクトリトラバーサル防止
        if not os.path.abspath(filepath).startswith(os.path.abspath(self.output_dir)):
            return None
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)
                rows = list(reader)
            
            return {
                'filename': filename,
                'headers': headers,
                'rows': rows,
                'row_count': len(rows),
                'column_count': len(headers),
            }
        except Exception as e:
            return None

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        サマリー統計を計算
        
        Returns:
            Dict: 統計情報
        """
        csv_files = self.get_csv_files()
        
        events_count = len([f for f in csv_files if f['file_type'] == 'events'])
        summary_count = len([f for f in csv_files if f['file_type'] == 'summary'])
        total_size = sum(f['size'] for f in csv_files)
        
        # 最新のサマリーファイルから統計を取得
        summary_files = [f for f in csv_files if f['file_type'] == 'summary']
        
        latest_stats = None
        if summary_files:
            latest_file = summary_files[0]['filename']
            data = self.read_csv_file(latest_file)
            if data:
                latest_stats = {
                    'filename': latest_file,
                    'metrics': {
                        row[0]: row[1] for row in data['rows']
                    }
                }
        
        return {
            'total_csv_files': len(csv_files),
            'events_files': events_count,
            'summary_files': summary_count,
            'total_size_bytes': total_size,
            'file_types': {
                'events': events_count,
                'summary': summary_count,
                'kana_analysis': len([f for f in csv_files if f['file_type'] == 'kana_analysis']),
            },
            'latest_summary': latest_stats,
        }

    def delete_csv_file(self, filename: str) -> bool:
        """
        CSVファイルを削除
        
        Args:
            filename: ファイル名
            
        Returns:
            bool: 削除成功の有無
        """
        filepath = os.path.join(self.output_dir, filename)
        
        # セキュリティチェック
        if not os.path.abspath(filepath).startswith(os.path.abspath(self.output_dir)):
            return False
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception:
            pass
        
        return False

    def export_statistics_summary(self) -> Dict[str, Any]:
        """
        統計情報をエクスポート
        
        Returns:
            Dict: エクスポート用統計データ
        """
        csv_files = self.get_csv_files()
        
        # セッション別に統計をグループ化
        session_stats = {}
        
        for csv_file in csv_files:
            if csv_file['file_type'] == 'summary':
                filename = csv_file['filename']
                # ファイル名から日時を抽出：typing_summary_YYYYMMDD_HHMMSS.csv
                if 'typing_summary_' in filename:
                    timestamp = filename.replace('typing_summary_', '').replace('.csv', '')
                    
                    data = self.read_csv_file(filename)
                    if data:
                        metrics = {}
                        for row in data['rows']:
                            if len(row) >= 2:
                                metrics[row[0]] = row[1]
                        
                        session_stats[timestamp] = {
                            'filename': filename,
                            'metrics': metrics,
                            'created': csv_file['created_time'],
                        }
        
        return {
            'total_sessions': len(session_stats),
            'sessions': session_stats,
        }
