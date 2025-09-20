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
        go projectroom3
        look around
        take hard disk
        back

        # StudyLandscape(here it won't work, need manual tweaks)
        go studylandscape
        approach lab2003

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


class TestBeatability:
    @pytest.mark.parametrize("commands,expected_room", BEATABLE_SCENARIOS)
    def test_simplest_way(
        self, default_blank_state_for_startup, commands, expected_room, capsys
    ):
        result, output, final_state = run_game_with_commands(
            commands, main, default_blank_state_for_startup, capsys
        )
        # Corridor part
        assert "manual" in final_state.get("inventory")
        # FrontDeskOffice part
        assert "battery" in final_state["inventory"], (
            f"the returned inventory: {final_state['inventory']}"
        )

        # Classroom2015 part
        assert final_state["visited"]["lab"], "lab challenge is not closed"

        # projectroom3 part
        assert "Hard Disk" in final_state["inventory"], (
            f"the returned inventory: {final_state['inventory']}"
        )

        # lab part
        assert final_state.get("inventory").get("security_key")
        assert "Have you received the security key" in output, "no finished lab"
        assert result == "corridor", f"the end result is not corridor: {result}"
