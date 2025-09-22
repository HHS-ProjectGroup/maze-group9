import pytest
from rooms.projectroom3 import enterProjectRoom3, ENTRY_KEYCARD
from tests.e2e.runner import run_game_with_commands

ACCESSIBILITY_SCENARIOS = [
    (["?", "look around", "back"], "corridor"),
    (["look around", "go corridor"], "corridor"),
    (["look around", "back"], "corridor"),
    (["go random"], None),
    (["go frontdeskoffice"], None),
    (["go studylandscape"], None),
    (["go lab03"], None),
    (["go classroom2015"], None),
    (
        [
            "look around",
            "take hard disk",
            "back",
        ],
        "corridor",
    ),
    (
        [
            "take hard disk",
            "go random",
        ],
        None,
    ),
]


class TestProjectRoom3:
    @pytest.mark.parametrize("commands,expected_room", ACCESSIBILITY_SCENARIOS)
    def test_exit_accessibility_with_battery(
        self, default_blank_state_for_startup, commands, expected_room, capsys
    ):
        default_blank_state_for_startup["flags"] = {'projectroom3_solved': True, 'projectroom3_reward_taken': False}
        default_blank_state_for_startup["inventory"].append(ENTRY_KEYCARD)
        result, output, final_state = run_game_with_commands(
            commands, enterProjectRoom3, default_blank_state_for_startup, capsys
        )

        assert result == expected_room
        if "take hard disk" in commands:
            assert "hard disk" in final_state["inventory"], (
                f"the returned inventory: {final_state['inventory']}"
            )
