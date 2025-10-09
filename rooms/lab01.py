import sys
from .constants import ROOM7

def enter_lab01(state):
    print("You beat the game.")
    try:
        # Mark the game as beaten so the leaderboard can be updated in main
        if isinstance(state, dict):
            state["game_beaten"] = True
    finally:
        sys.exit()