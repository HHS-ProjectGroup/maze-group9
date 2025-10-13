import pytest
from rooms.corridor import enter_corridor

from tests.e2e.runner import run_game_with_commands

ACCESSIBILITY_SCENARIOS = [
    (["look around", "take manual", "go classroom2015"], "classroom2015"),
    (["look around", "take manual", "go projectroom3"], "projectroom3"),
    (["go frontdeskoffice"], "frontdeskoffice"),
    (["look around", "take manual", "go corridor"], None),
    (["look around", "take manual", "go lab03"], None),
    (["look around", "take manual", "go studylandscape"], "studylandscape"),
]


class TestCorridor:
    @pytest.mark.parametrize("commands,expected_room", ACCESSIBILITY_SCENARIOS)
    def test_corridor_path(
        self, default_blank_state_for_startup, commands, expected_room, capsys
    ):
        result, output, final_state = run_game_with_commands(
            commands, enter_corridor, default_blank_state_for_startup, capsys
        )

        assert result == expected_room
        if "take manual" in commands:
            assert "manual" in final_state["inventory"]
            assert final_state["health"] == 3
