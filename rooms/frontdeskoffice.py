# -----------------------------------------------------------------------------
# File: frontdeskoffice.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------

import random
import sys
from persistence import save_state, clear_state, reset_state
from constants import ITEM_2, ROOM2


def _ensure_front_desk_state(state):
    # Initialize persistent state for this room
    if ROOM2 not in state["visited"]:
        state["visited"][ROOM2] = False
    if ROOM2 not in state:
        state["frontdesk_question"] = None  # will store dict with q, options, correct ('a'..'d')
    if "frontdesk_reward_spawned" not in state:
        state["frontdesk_reward_spawned"] = False


def _question_pool():
    # Returns a list of questions with options and correct key
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
        },
        {
            "q": "Which country is Paris the capital of?",
            "options": {
                "a": "Spain",
                "b": "Italy",
                "c": "France",
                "d": "Belgium",
            },
            "correct": "c",
        },
        {
            "q": "What is the capital of Japan?",
            "options": {
                "a": "Kyoto",
                "b": "Tokyo",
                "c": "Osaka",
                "d": "Hiroshima",
            },
            "correct": "b",
        },
    ]


def _print_room_header(state):
    print("\nYou step into the Front Desk Office.")
    print("\nA holographic desk shimmers faintly, and a Cyber Receptionist flickers with glitchy static.")
    print("\nBehind the desk, a sealed access panel hums silently.")

    if not state["visited"][ROOM2]:
        print("\n[Cyber Receptionist]: “Weeeelc-co-meee, challenger. To rec-ceeeive powerrrr, you must answerrrr… correctly.”")


def _pick_new_question(state):
    state["frontdesk_question"] = random.choice(_question_pool())


def _show_question(state):
    q = state["frontdesk_question"]
    if not q:
        _pick_new_question(state)
        q = state["frontdesk_question"]
    print(f"\nQuestion: {q['q']}")
    print(f" a) {q['options']['a']}")
    print(f" b) {q['options']['b']}")
    print(f" c) {q['options']['c']}")
    print(f" d) {q['options']['d']}")


def _print_commands(state):
    print("\nAvailable commands:")
    if not state["visited"][ROOM2]:
        print("- answer <a/b/c/d>    : Answer the current question.")
    if state["visited"][ROOM2] and state["frontdesk_reward_spawned"] and ITEM_2 not in state["inventory"]:
        print(f"- take {ITEM_2}         : Pick up the {ITEM_2} reward.")
    print("- leave                : Exit to the corridor.")
    print("- ?                    : Show this help message.")
    print("- look around          : Reprint description and your options.")
    print("- pause                : Save and exit (pause the game).")
    print("- quit                 : Quit without saving.")


def enterFrontDeskOffice(state):
    _ensure_front_desk_state(state)

    # Always show header on entering
    _print_room_header(state)

    # If solved previously, show post-completion greeting and commands, no questions
    if state["visited"][ROOM2]:
        print("\n[Cyber Receptionist]: “W-e-eee...lc---ome b...ba-ck, ch-ch-challeng-er...”")
        _print_commands(state)
    else:
        # First-time entry: select or show a question
        if not state["frontdesk_question"]:
            _pick_new_question(state)
        _show_question(state)
        _print_commands(state)

    # Main command loop for the room
    while True:
        command = input("\n> ").strip().lower()

        if command in ("?", "help"):
            _print_commands(state)
            continue

        if command == "look around":
            _print_room_header(state)
            if not state["visited"][ROOM2]:
                _show_question(state)
            _print_commands(state)
            continue

        if command == "leave" or command == "go corridor" or command == "back":
            print("You step away from the holographic desk and return to the corridor.")
            state["previous_room"] = ROOM2
            return "corridor"

        if command.startswith("answer "):
            choice = command.split(" ", 1)[1].strip()
            if state["visited"][ROOM2]:
                print("You already proved your worth. No more questions.")
                continue
            if choice not in ["a", "b", "c", "d"]:
                print("Please answer with: answer a | answer b | answer c | answer d")
                continue
            q = state["frontdesk_question"]
            if not q:
                _pick_new_question(state)
                q = state["frontdesk_question"]
            if choice == q["correct"]:
                print("\n[Cyber Receptionist]: “Corrrrrect... ch-challenger. Acc-cccept your re-ward...”")
                print(f"The Cyber Receptionist extends a shimmering holo-hand and gently places a {ITEM_2} on the desk in front of you.")
                print(f"The {ITEM_2} hums softly with stored energy.")
                # Spawn {ITEM_2} in the room (once)
                state["frontdesk_reward_spawned"] = True
                state["visited"][ROOM2] = True
                # After success, no new questions; show that {ITEM_2} can be taken
                _print_commands(state)
            else:
                print("\n[Cyber Receptionist]: “Inc-c-c-correct. You are unworthy. EJECTING…”")
                print("You are flung out into the corridor!")
                state["frontdesk_question"] = None  # ensure a fresh random on next entry
                state["previous_room"] = ROOM2
                return "corridor"
            continue

        if command.startswith("take "):
            item = command[5:].strip().lower()
            if item == ITEM_2:
                if state["visited"][ROOM2] and state["frontdesk_reward_spawned"]:
                    if ITEM_2 in state["inventory"]:
                        print(f"You already took the {ITEM_2}.")
                    else:
                        print(f"🔋 You take the {ITEM_2} and store it in your backpack.")
                        state["inventory"].append(ITEM_2)
                        # {ITEM_2} picked up; keep reward flag so no new {ITEM_2} spawns
                    _print_commands(state)
                else:
                    print(f"There is no {ITEM_2} available right now.")
            else:
                print(f"There is no '{item}' to take here.")
            continue

        if command == "pause":
            print("⏸️ Game paused. Your progress has been saved.")
            try:
                save_state(state)
            finally:
                sys.exit()

        if command == "quit":
            print("👋 You leave the front desk behind. Progress not saved.")
            try:
                clear_state()
                reset_state(state)
            finally:
                sys.exit()

        print("❓ Unknown command. Type '?' to see available commands.")
