import pytest
from rooms.lab03 import enter_lab03
from tests.e2e.runner import run_game_with_commands

ACCESSIBILITY_SCENARIOS = [
    (["look around", "leave"], None),
    (["look around", "go corridor"], "corridor"),
    (["go frontdeskoffice"], None),
    (["look around", "take something", "go corridor"], "corridor"),
    (["look around", "enter the pc", "quit", "yes", "Caesar", "go lab03"], "corridor"),
    (
        ["look around", "enter the pc", "quit", "yes", "Caesar", "go corridor"],
        "corridor",
    ),
    (["take manual", "go studylandscape"], None),
]


class TestLab:
    @pytest.mark.parametrize("commands,expected_room", ACCESSIBILITY_SCENARIOS)
    def test_leave(
        self, default_blank_state_for_startup, commands, expected_room, capsys
    ):
        default_blank_state_for_startup["visited"]["lab"] = False
        result, output, final_state = run_game_with_commands(
            commands, enter_lab03, default_blank_state_for_startup, capsys
        )

        assert result == expected_room
        if "enter the pc" in commands:
            assert "security_key" in final_state["inventory"]
