import os
from rooms import (
    enterClassroom2015,
    enterCorridor,
    enterFrontDeskOffice,
    enterLab03,
    enterLab01,
    enterProjectRoom3,
    enterStudyLandscape,

)
from persistence import load_state, get_default_state
from leaderboard import print_leaderboard, append_result, GameTimer


state = get_default_state()
def _get_player_name() -> str:
    # Avoid blocking test automation
    import sys
    if os.getenv("MAZE_AUTOMATED_TESTING") == "1":
        return os.getenv("MAZE_TEST_PLAYER", "TestUser")
    # If stdin is not interactive (e.g., during automated tests), avoid prompting
    try:
        if not sys.stdin or not sys.stdin.isatty():
            return "Player"
    except Exception:
        return "Player"
    try:
        name = input("Enter your name for the leaderboard (leave empty for 'Player'): ").strip()
        return name if name else "Player"
    except Exception:
        return "Player"



def main(state):
    print(
        "****************************************************************************"
    )
    print(
        "*                      Welcome to the School Maze!                         *"
    )
    print(
        "*        Your goal is to explore all important rooms in the school.        *"
    )
    print(
        "*    You may need to solve challenges to collect items and unlock rooms.   *"
    )
    print(
        "*               Once you've visited all rooms, you win!                    *"
    )
    print(
        "****************************************************************************"
    )

    while True:
        current = state["current_room"]

        # Selim
        if current == "corridor":
            state["current_room"] = enterCorridor(state)

        # Alex
        elif current == "studylandscape":
            state["current_room"] = enterStudyLandscape(state)

        # Gleb
        elif current == "lab03":
            state["current_room"] = enterLab03(state)

        # Arda
        elif current == "frontdeskoffice":
            state["current_room"] = enterFrontDeskOffice(state)

        # Sil
        elif current == "classroom2015":
            state["current_room"] = enterClassroom2015(state)

        # Bianca
        elif current == "projectroom3":
            state["current_room"] = enterProjectRoom3(state)

        elif current == "lab01":
            state["current_room"] = enterLab01(state)

        else:
            print("Unknown room. Exiting game.")
            break


if __name__ == "__main__":
    # Show leaderboard before starting
    print_leaderboard()

    # Start game timer
    timer = GameTimer()
    timer.start()

    # Always attempt to load previous state saved via 'pause'; if none, start fresh
    loaded = load_state()
    if loaded:
        state = loaded
        print("[Loaded saved game state from database]")
    try:
        main(state)
    except:pass
    finally:
    seconds = timer.stop()
    name = _get_player_name()
    # Ensure state is defined and score exists
    try:
        score = int(state.get("score", 0)) if isinstance(state, dict) else 0
    except Exception:
        score = 0
    append_result(name=name, score=score, seconds=float(seconds))
    print("\nYour result has been saved to the leaderboard. Thank you for playing!")