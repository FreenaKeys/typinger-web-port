"""
test_core_modules.py
コアモジュールのユニットテスト
"""

import pytest
from core.romaji_converter import RomajiConverter, ConvertStatus
from core.typing_judge import TypingJudge, JudgeResult
from core.statistics import StatisticsCalculator, KeyEvent, EventType
from core.scenario_manager import ScenarioManager


class TestRomajiConverter:
    def setup_method(self):
        self.converter = RomajiConverter()

    def test_basic_conversion(self):
        result = self.converter.convert("ka")
        assert result.status == ConvertStatus.MATCHED
        assert result.kana == "か"
        assert result.consumed == "ka"

    def test_partial_match(self):
        result = self.converter.convert("k")
        assert result.status == ConvertStatus.PARTIAL

    def test_no_match(self):
        result = self.converter.convert("xyz")
        assert result.status == ConvertStatus.NO_MATCH

    def test_multi_char_conversion(self):
        result = self.converter.convert("sha")
        assert result.status == ConvertStatus.MATCHED
        assert result.kana == "しゃ"

    def test_can_convert(self):
        assert self.converter.can_convert("ka") == True
        assert self.converter.can_convert("xyz") == False

    def test_to_romaji(self):
        assert RomajiConverter.to_romaji("か") == "ka"
        assert RomajiConverter.to_romaji("しゃ") == "sha"


class TestTypingJudge:
    def setup_method(self):
        self.judge = TypingJudge("こんにちは", "konnichiha")

    def test_correct_char(self):
        result = self.judge.judge_char("k")
        assert result == JudgeResult.CORRECT
        assert self.judge.get_current_position() == 1
        assert self.judge.get_correct_count() == 1

    def test_incorrect_char(self):
        result = self.judge.judge_char("x")
        assert result == JudgeResult.INCORRECT
        assert self.judge.get_current_position() == 0
        assert self.judge.get_incorrect_count() == 1

    def test_sequence_input(self):
        for char in "konni":
            result = self.judge.judge_char(char)
            assert result == JudgeResult.CORRECT

        assert self.judge.get_current_position() == 5

    def test_accuracy(self):
        self.judge.judge_char("k")
        self.judge.judge_char("o")
        self.judge.judge_char("x")  # 誤入力

        accuracy = self.judge.get_accuracy()
        assert accuracy == 2 / 3  # 2/3 = 0.667

    def test_completion(self):
        for char in "konnichiha":
            self.judge.judge_char(char)

        assert self.judge.is_completed() == True

    def test_remaining_rubi(self):
        self.judge.judge_char("k")
        self.judge.judge_char("o")
        remaining = self.judge.get_remaining_rubi()
        assert remaining == "nnichiha"


class TestStatisticsCalculator:
    def setup_method(self):
        self.calc = StatisticsCalculator()

    def test_add_events(self):
        events = [
            KeyEvent(EventType.KEY_DOWN, 0, 75, 'k'),
            KeyEvent(EventType.KEY_DOWN, 100000, 79, 'o'),
            KeyEvent(EventType.KEY_DOWN, 200000, 78, 'n'),
        ]

        for event in events:
            self.calc.add_event(event)

        assert len(self.calc.events) == 3

    def test_calculate_statistics(self):
        events = [
            KeyEvent(EventType.KEY_DOWN, 0, 75, 'k'),
            KeyEvent(EventType.KEY_DOWN, 100000, 79, 'o'),
            KeyEvent(EventType.KEY_DOWN, 200000, 78, 'n'),
        ]

        for event in events:
            self.calc.add_event(event)

        stats = self.calc.calculate_statistics(3, 10)

        assert stats.total_key_count == 3
        assert stats.correct_key_count == 3
        assert stats.total_duration == 200000


class TestScenarioManager:
    def setup_method(self):
        self.manager = ScenarioManager("scenario")

    def test_get_available_scenarios(self):
        scenarios = self.manager.get_available_scenarios()
        # Scenario directory may be empty in test environment
        assert isinstance(scenarios, list)

    def test_load_nonexistent_scenario(self):
        result = self.manager.load_scenario("nonexistent.json")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
