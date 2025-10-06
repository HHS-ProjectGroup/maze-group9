import pytest

from main import main
from tests.e2e.runner import run_game_with_commands

import textwrap

BEATABLE_SCENARIOS = [
    (
        textwrap.dedent(
            """
        # FrontDeskOffice
        take manual
        go frontdeskoffice
        look around
        answer a
        take battery
        leave

        # Classroom2015
        go classroom2015
        look around
        approach cyborg
        a
        b
        a
        take yellow keycard
        leave

        # Project Room 3
        look around
        go projectroom3
        look around
        take hard disk
        back

        # StudyLandscape(here it won't work, need manual tweaks)
        go studylandscape
        go lab03

        # Lab2003
        look around
        enter the pc
        quit
        yes
        Caesar
        go corridor
        """
        )
        .strip()
        .splitlines(),
        "corridor",
    )
]


def normalize_commands(commands: list[str]) -> list[str]:
    """Фильтрует комментарии (# ...) из сценариев"""
    return [cmd for cmd in commands if not cmd.strip().startswith("#") and cmd != ""]


class TestBeatability:
    @pytest.mark.parametrize("commands,expected_room", BEATABLE_SCENARIOS)
    def test_simplest_way(
        self, default_blank_state_for_startup, commands, expected_room, capsys
    ):
        result, output, final_state = run_game_with_commands(
            normalize_commands(commands), main, default_blank_state_for_startup, capsys
        )
        noutput = output.out
        # Corridor part
        assert "manual" in final_state.get("inventory")
        # FrontDeskOffice part
        assert "battery" in final_state["inventory"], (
            f"the returned inventory: {final_state['inventory']}"
        )

        # Classroom2015 part(without mocking will assert)
        assert final_state["visited"]["classroom2015"], (
            f"classroom2015 challenge is not closed: state: {final_state}"
        )

        # projectroom3 part
        assert "You tap the Classroom2025 Keycard." in output, (
            f"We must have obtained access by this point: "
            f"{final_state['inventory']}\n\n"
            f"--- OUTPUT ---\n{noutput}\n--- END OUTPUT ---"
        )
        assert "hard disk" in final_state["inventory"], (
            f"the returned inventory: {final_state['inventory']}"
        )

        # lab part
        assert final_state.get("inventory").get("security_key")
        assert "Have you received the security key" in output, "no finished lab"
        assert result == "corridor", f"the end result is not corridor: {result}"
