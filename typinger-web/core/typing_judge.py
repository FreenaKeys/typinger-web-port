"""
typing_judge.py
タイピング判定ロジック

用語解説:
- rubi（ルビ）: 目標となるローマ字入力列（例: "konnichiwa"）
- 逐次判定（Incremental Judgment）: 1文字ずつ入力を照合
"""

from enum import Enum
from typing import List


class JudgeResult(Enum):
    CORRECT = "correct"          # 正解
    INCORRECT = "incorrect"      # 不正解
    ALREADY_DONE = "already_done"  # すでに完了済み（追加入力不要）


class TypingJudge:
    """タイピング判定クラス"""

    def __init__(self, target_text: str, target_rubi: str):
        """
        コンストラクタ
        
        Args:
            target_text: 目標テキスト（日本語）
            target_rubi: 目標ルビ（ローマ字）
        """
        self.target_text = target_text
        self.target_rubi = target_rubi.lower()  # 小文字正規化
        self.current_position = 0
        self.correct_count = 0
        self.incorrect_count = 0
        self.input_history: List[char] = []

    def judge_char(self, input_char: str) -> JudgeResult:
        """
        1文字判定
        
        Args:
            input_char: 入力文字
            
        Returns:
            JudgeResult: 判定結果
        """
        if self.is_completed():
            return JudgeResult.ALREADY_DONE
        
        # 入力文字を小文字に正規化
        input_char_lower = input_char.lower()
        
        # 現在位置の目標文字と比較
        if self.current_position < len(self.target_rubi):
            target_char = self.target_rubi[self.current_position]
            
            if input_char_lower == target_char:
                self.correct_count += 1
                self.current_position += 1
                self.input_history.append(input_char)
                return JudgeResult.CORRECT
            else:
                self.incorrect_count += 1
                self.input_history.append(input_char)
                return JudgeResult.INCORRECT
        
        return JudgeResult.ALREADY_DONE

    def get_current_position(self) -> int:
        """現在位置を取得"""
        return self.current_position

    def get_target_length(self) -> int:
        """目標ルビ長を取得"""
        return len(self.target_rubi)

    def get_correct_count(self) -> int:
        """正解数を取得"""
        return self.correct_count

    def get_incorrect_count(self) -> int:
        """不正解数を取得"""
        return self.incorrect_count

    def is_completed(self) -> bool:
        """完了判定"""
        return self.current_position >= len(self.target_rubi)

    def get_accuracy(self) -> float:
        """
        正解率を取得
        
        Returns:
            float: 正解率（0.0 ～ 1.0）
        """
        total = self.correct_count + self.incorrect_count
        if total == 0:
            return 0.0
        return self.correct_count / total

    def get_remaining_rubi(self) -> str:
        """未入力のルビ部分を取得"""
        return self.target_rubi[self.current_position:]

    def get_target_text(self) -> str:
        """目標テキストを取得"""
        return self.target_text

    def get_target_rubi(self) -> str:
        """目標ルビを取得"""
        return self.target_rubi

    def reset(self):
        """リセット"""
        self.current_position = 0
        self.correct_count = 0
        self.incorrect_count = 0
        self.input_history = []

    def get_progress_display(self) -> dict:
        """進捗を表示用フォーマットで取得"""
        return {
            "target_text": self.target_text,
            "target_rubi": self.target_rubi,
            "current_position": self.current_position,
            "target_length": len(self.target_rubi),
            "progress_percent": (self.current_position / len(self.target_rubi) * 100) if self.target_rubi else 0,
            "correct_count": self.correct_count,
            "incorrect_count": self.incorrect_count,
            "accuracy": self.get_accuracy(),
            "remaining_rubi": self.get_remaining_rubi(),
            "is_completed": self.is_completed(),
        }
