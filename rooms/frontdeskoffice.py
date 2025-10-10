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
from rooms.texts import FRNT_DSK_FAILED_CAPCHA, FRNT_DSK_LOOK_AROUND, FRNT_DSK_SOLVED_CAPCHA, type_rich
from .constants import ITEM_2, ROOM2
from .utils import display_status, handle_help_generic


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
    if state["visited"][ROOM2]:
        type_rich("""The desk looks the same as before, but the holographic glow has dimmed.
The air smells faintly of burnt circuitry.
The coffee is cold now.
The terminal still sits there, logged out and unresponsive — like the room itself is done talking.
The battery slot under the desk is empty.""")

    else:
     type_rich("""You step into the Front Desk Office.
The air feels warmer here, as if the ventilation is still running.
A single desk stands in the center, covered with faint holographic residue.
A terminal hums quietly — still logged in, its display frozen on a half-written email.
Papers and notes are scattered around; a coffee cup rests by the keyboard, still half full.
Whoever worked here must’ve left in a hurry.""")

def _look_around():
    FRNT_DSK_LOOK_AROUND()


def _pick_new_question(state):
    state["frontdesk_question"] = random.choice(_question_pool())


def _show_question(state):
    q = state["frontdesk_question"]
    if not q:
        _pick_new_question(state)
        q = state["frontdesk_question"]
    type_rich(f"Question: {q['q']}", dialog=True)
    type_rich(f" a) {q['options']['a']}", dialog=True)
    type_rich(f" b) {q['options']['b']}", dialog=True)
    type_rich(f" c) {q['options']['c']}", dialog=True)
    type_rich(f" d) {q['options']['d']}", dialog=True)


def _print_commands(state):
    if not state["visited"][ROOM2]:
        handle_help_generic(ROOM2, specifics={"answer <a/b/c/d>": "answer the current question."})
    elif state["visited"][ROOM2] and state["frontdesk_reward_spawned"] and ITEM_2 not in state["inventory"]:
        handle_help_generic(ROOM2, specifics={f"take {ITEM_2}": f"Pick up the {ITEM_2} reward."})
    else:
        handle_help_generic(ROOM2)

def enter_frontdeskoffice(state):
    _ensure_front_desk_state(state)

    # Always show header on entering
    _print_room_header(state)

    # If solved previously, show post-completion greeting and commands, no questions
    if state["visited"][ROOM2]:
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
            _look_around()
            if not state["visited"][ROOM2]:
                _show_question(state)
            _print_commands(state)
            continue

        if command == "leave" or command == "go corridor" or command == "back":
            type_rich("You step away from the holographic desk and return to the corridor.")
            state["previous_room"] = ROOM2
            return "corridor"

        if command.startswith("answer "):
            choice = command.split(" ", 1)[1].strip()
            if state["visited"][ROOM2]:
                type_rich("No more questions to answer.")
                continue
            if choice not in ["a", "b", "c", "d"]:
                type_rich("Please answer with: answer a | answer b | answer c | answer d")
                continue
            q = state["frontdesk_question"]
            if not q:
                _pick_new_question(state)
                q = state["frontdesk_question"]
            if choice == q["correct"]:
                FRNT_DSK_SOLVED_CAPCHA()
                # Spawn {ITEM_2} in the room (once)
                state["frontdesk_reward_spawned"] = True
                state["visited"][ROOM2] = True
                # After success, no new questions; show that {ITEM_2} can be taken
                _print_commands(state)
            else:
                FRNT_DSK_FAILED_CAPCHA()
                state["frontdesk_question"] = None  # ensure a fresh random on next entry
                state["previous_room"] = ROOM2
                return "corridor"
            continue

        if command.startswith("take "):
            item = command[5:].strip().lower()
            if item == ITEM_2:
                if state["visited"][ROOM2] and state["frontdesk_reward_spawned"]:
                    if ITEM_2 in state["inventory"]:
                        type_rich(f"You already took the {ITEM_2}.")
                    else:
                        type_rich(f"🔋 You take the {ITEM_2} and store it in your backpack.")
                        state["inventory"].append(ITEM_2)
                        # {ITEM_2} picked up; keep reward flag so no new {ITEM_2} spawns
                    _print_commands(state)
                else:
                    type_rich(f"There is no {ITEM_2} available right now.")
            else:
                type_rich(f"There is no '{item}' to take here.")
            continue

        if command == "display status":
            display_status(state)
            continue

        if command == "pause":
            type_rich("⏸️ Game paused. Your progress has been saved.")
            try:
                save_state(state)
            finally:
                sys.exit()

        if command == "quit":
            type_rich("👋 You leave the front desk behind. Progress not saved.")
            try:
                clear_state()
                reset_state(state)
            finally:
                sys.exit()

        type_rich("❓ Unknown command. Type '?' to see available commands.")
