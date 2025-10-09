import os
from rooms import (
    enter_classroom2015,
    enter_corridor,
    enter_frontdeskoffice,
    enter_lab03,
    enter_lab01,
    enter_projectroom3,
    enter_studylandscape,
    constants
)
from rooms.constants import ROOM1, ROOM2, ROOM3, ROOM4, ROOM5, ROOM6, ROOM7
from persistence import load_state, get_default_state, save_state
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
        if current == ROOM1:
            state["current_room"] = enter_corridor(state)

        # Arda
        elif current == ROOM2:
            state["current_room"] = enter_frontdeskoffice(state)

        # Sil
        elif current == ROOM3:
            state["current_room"] = enter_classroom2015(state)

        # Bianca
        elif current == ROOM4:
            state["current_room"] = enter_projectroom3(state)

        # Alex
        elif current == ROOM5:
            state["current_room"] = enter_studylandscape(state)

        # Gleb
        elif current == ROOM6:
            state["current_room"] = enter_lab03(state)

        elif current == ROOM7:
            state["current_room"] = enter_lab01(state)

        else:
            print("Unknown room. Exiting game.")
            break


if __name__ == "__main__":
    # Show leaderboard before starting
    print_leaderboard()

    # Start game timer for this session
    timer = GameTimer()
    timer.start()

    # Always attempt to load previous state saved via 'pause'; if none, start fresh
    loaded = load_state()
    if loaded:
        state = loaded
        print("[Loaded saved game state from database]")

    try:
        main(state)
    except BaseException:
        # Swallow SystemExit from room handlers (pause/quit) and any other exceptions
        pass
    finally:
        # Update accumulated elapsed time into state and persist
        try:
            session_seconds = float(timer.stop())
        except Exception:
            session_seconds = 0.0
        try:
            prev = float(state.get("elapsed_seconds", 0.0)) if isinstance(state, dict) else 0.0
        except Exception:
            prev = 0.0
        total_elapsed = max(0.0, prev + session_seconds)
        if isinstance(state, dict):
            state["elapsed_seconds"] = total_elapsed
            # Ensure score key exists for persistence
            state.setdefault("score", 0)
        # Save the latest state (including time/score) so pause/quit resumes correctly
        try:
            save_state(state)
        except Exception:
            pass

        # Only record leaderboard when the game has been beaten
        beaten = bool(state.get("game_beaten", False)) if isinstance(state, dict) else False
        if beaten:
            name = _get_player_name()
            try:
                score_val = int(state.get("score", 0)) if isinstance(state, dict) else 0
            except Exception:
                score_val = 0
            append_result(name=name, score=score_val, seconds=float(total_elapsed))
            print("\nYour result has been saved to the leaderboard. Thank you for playing!")
        else:
            # Don’t touch leaderboard on pause/quit before victory
            pass