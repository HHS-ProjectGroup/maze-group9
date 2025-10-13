import pytest
from rooms.frontdeskoffice import enter_frontdeskoffice
from tests.e2e.runner import run_game_with_commands

ACCESSIBILITY_SCENARIOS = [
    (["?", "look around", "leave"], "corridor"),
    (["look around", "go corridor"], "corridor"),
    (["look around", "back"], "corridor"),
    (["go random"], None),
    (["look around", "answer a", "take battery", "leave"], "corridor"),
    (
        [
            "look around",
            "answer a",
            "take battery",
            "go lab03",
            "go projectroom3",
            "go classroom2015",
            "go frontdeskoffice",
            "go studylandscape",
        ],
        None,
    ),
]


def deterministic_question():
    return [
        {
            "q": "What is the capital of Germany?",
            "options": {
                "a": "Berlin",
                "b": "Munich",
                "c": "Frankfurt",
                "d": "Hamburg",
            },
            "correct": "a",
        }
    ]


@pytest.fixture(autouse=True)
def patch_frontdesk_quiz_and_answer(monkeypatch):
    monkeypatch.setattr(
        "rooms.frontdeskoffice._question_pool", lambda: deterministic_question()
    )


class TestFrontDesk:
    @pytest.mark.parametrize("commands,expected_room", ACCESSIBILITY_SCENARIOS)
    def test_exit_accessibility(
        self, default_blank_state_for_startup, commands, expected_room, capsys
    ):
        default_blank_state_for_startup["current_room"] = "frontdeskoffice"
        result, output, final_state = run_game_with_commands(
            commands, enter_frontdeskoffice, default_blank_state_for_startup, capsys
        )

        if final_state["frontdesk_question"]:
            assert final_state["frontdesk_question"]["correct"] == "a"
        assert result == expected_room
        if "take battery" in commands:
            assert "battery" in final_state["inventory"], (
                f"the returned inventory: {final_state['inventory']}"
            )
