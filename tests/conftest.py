import random
from rooms.corridor import generate_quadratic_inequality
import copy
import pytest

"""Other files can use fixtures from here"""


@pytest.fixture()
def default_blank_state_for_startup():
    d = {
        "current_room": "corridor",
        "previous_room": "corridor",
        "visited": {
            "classroom2015": False,
            "projectroom3": False,
            "frontdeskoffice": False,
            "corridor": [True, 3],
            "lab": False,
        },
        "inventory": [],
        "health": 3,
    }
    return copy.deepcopy(d)


@pytest.fixture(autouse=True)
def patch_frontdesk_quiz_and_answer(monkeypatch):
    monkeypatch.setattr(
        "rooms.frontdeskoffice._question_pool", lambda: deterministic_question()
    )


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
def patch_corridor_random_and_quiz(monkeypatch):
    # Don't enter minigame
    monkeypatch.setattr(random, "random", lambda: 1.0)
    # If case enter anlways return True
    monkeypatch.setattr(generate_quadratic_inequality, "__call__", lambda state: True)
