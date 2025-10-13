import pytest
from rooms.classroom2015 import enter_classroom2015
from tests.e2e.runner import run_game_with_commands

ACCESSIBILITY_SCENARIOS = [
    (["?", "look around", "leave"], "corridor"),
    (["look around", "go corridor"], "corridor"),
    (["look around", "back"], "corridor"),
    (["go random"], None),
    (["go frontdeskoffice"], None),
    (["go studylandscape"], None),
    (["go lab03"], None),
    (["go projectroom3"], None),
    (
        [
            "look around",
            "approach cyborg",
            "a",
            "b",
            "a",
            "take yellow keycard",
            "leave",
        ],
        "corridor",
    ),
    (
        [
            "look around",
            "approach cyborg",
            "a",
            "b",
            "a",
            "take yellow keycard",
            "go random",
        ],
        None,
    ),
    (["look around", "approach cyborg", "a", "b", "a", "go random"], None),
    (["look around", "approach cyborg", "a", "b", "a", "leave"], "corridor"),
]


class TestClassRoom2015:
    @pytest.mark.parametrize("commands,expected_room", ACCESSIBILITY_SCENARIOS)
    def test_exit_accessibility_no_battery(
        self, default_blank_state_for_startup, commands, expected_room, capsys
    ):
        default_blank_state_for_startup["current_room"] = "classroom2015"
        result, output, final_state = run_game_with_commands(
            commands, enter_classroom2015, default_blank_state_for_startup, capsys
        )

        assert result == expected_room
        if "take yellow keycard" in commands:
            assert "yellow keycard" not in final_state["inventory"], (
                f"the returned inventory: {final_state['inventory']}"
            )

    @pytest.mark.parametrize("commands,expected_room", ACCESSIBILITY_SCENARIOS)
    def test_exit_accessibility_with_battery(
        self, default_blank_state_for_startup, commands, expected_room, capsys
    ):
        default_blank_state_for_startup["inventory"].append("battery")
        default_blank_state_for_startup["current_room"] = "classroom2015"
        result, output, final_state = run_game_with_commands(
            commands, enter_classroom2015, default_blank_state_for_startup, capsys
        )

        assert result == expected_room
        if "take yellow keycard" in commands:
            assert "yellow keycard" in final_state["inventory"], (
                f"the returned inventory: {final_state['inventory']}"
            )
