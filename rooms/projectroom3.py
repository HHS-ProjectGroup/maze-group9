# -----------------------------------------------------------------------------
# File: projectroom3.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------
# Testing git

import sys
import random
from persistence import get_default_state, save_state, clear_state, reset_state
from rooms.texts import PRJ3_DESC_0, PRJ3_DIALOG_ON_LEAVE, PRJ3_LOOK_AROUND, PRJ3_WELCOME_SOLVED, type_rich
from rooms.constants import ITEM_3, ITEM_4, ROOM1, ROOM4
from rooms.utils import display_status, handle_help_generic

ENTRY_KEYCARD = ITEM_3  # item needed to unlock the door
REWARD_ITEM   = ITEM_4  # reward given after solving

# Hangman-Lite settings
WORDS = [
    "protocol", "network", "hardware", "software", "debugger",
    "compiler", "variable", "function", "iterate", "package",
    "python", "student", "teacher", "project", "console"
]

MAX_ATTEMPTS  = 6            # wrong guesses allowed

def enter_projectroom3(state):
    state.setdefault("visited", {})
    state["visited"].setdefault(ROOM4, False)

    state.setdefault("inventory", [])
    state.setdefault("previous_room", ROOM1)

    state.setdefault("flags", {})
    state["flags"].setdefault("projectroom3_solved", False)
    state["flags"].setdefault("projectroom3_reward_taken", False)

    solved = state["flags"]["projectroom3_solved"]
    reward_taken = state["flags"]["projectroom3_reward_taken"]

    # ---------- gate: first-ever entry needs the keycard ----------
    if not state["visited"][ROOM4]:
        if ENTRY_KEYCARD not in state["inventory"]:
            type_rich("🔒 The blurred glass door of Project Room 3 blinks red. Probably you can't access it yet.")
            return ROOM1
        else:
            type_rich("🪪 Just as you approach it, the glass turnes transperent and lits up. The lock blinks green and the door slides open.")

    # ---------- room description ----------
    type_rich("🧩 You enter Project Room 3.")
    if solved:
        PRJ3_WELCOME_SOLVED()
    else:
        PRJ3_DESC_0()

    # mark as visited so the door gate won't repeat
    state["visited"][ROOM4] = True
    current_word = None
    if not state["flags"]["projectroom3_solved"]:
        current_word = random.choice(WORDS)

    # ---------- per-visit puzzle runtime (resets if you leave/fail) ----------
    attempts_left = MAX_ATTEMPTS  # player gets 6 mistakes
    revealed      = ["_" for _ in (current_word or "")]  # underscores for the chosen word
    guessed       = []            # letters tried
    puzzle_active = False         # becomes True after 'start challenge'

    # ---------------- helpers ----------------
    def show_help(): 
        specifics: dict ={
            "start challenge": "Begin/continue the hangman puzzle.",
            "guess <letter>":  "Guess one letter (a-z).",
            "solve <word>":  "Attempt the full word.", 
        }

        if state["flags"]["projectroom3_solved"]:
            specifics[f"take {REWARD_ITEM.lower()}"] = "Take the reward (after success)."

        handle_help_generic(ROOM4, specifics=specifics)

    def show_room(): #describe the room again, depends on the progress
        PRJ3_LOOK_AROUND()
        type_rich(f"- Inventory: {state["inventory"]}")

    def word_mask(): #return the word display , underscores + revealed letters
        return " ".join(revealed)

    def print_status(): #show the puzzle progress
        guessed_str = ", ".join(guessed) if guessed else "-"
        type_rich(f"Word: {word_mask()}   Attempts left: {attempts_left}   Guessed: {guessed_str}", dialog=True)

    def start_challenge(): #start the hangman puzzle
        nonlocal puzzle_active
        if state["flags"]["projectroom3_solved"]:
            type_rich("✅ The console is already unlocked.", dialog=True)
            return
        if not puzzle_active:
            puzzle_active = True
            type_rich("“Guess the hidden word. Use 'guess <letter>' or 'solve <word>'.”", dialog=True)
        print_status()

    def finish_success(): #when puzzle is solved correctly
        state["flags"]["projectroom3_solved"] = True
        type_rich("🎉 The console flashes green. WORD UNLOCKED.")
        if not state["flags"]["projectroom3_reward_taken"]:
            print(f"🏅 A compartment opens, revealing the {REWARD_ITEM}. Use 'take {REWARD_ITEM.lower()}'.")
        else:
            type_rich("The reward compartment is already empty.")

        PRJ3_DIALOG_ON_LEAVE()

    def fail_and_eject():#if puzzle fails, player is sent out
        type_rich("🚨 Alarms blare. The console locks and the door slides open. The room says: ")
        type_rich("'Return when you are ready.'", dialog=True)
        return ROOM1

    def handle_guess(letter): #process a single letter guess in hangman
        nonlocal attempts_left
        if state["flags"]["projectroom3_solved"]:
            type_rich("✅ Already solved.")
            return None
        if not puzzle_active:
            type_rich("No active puzzle. Use 'start challenge' first.")
            return None
        letter = letter.strip().lower()
        if len(letter) != 1 or not letter.isalpha():
            type_rich("Please guess a single letter (a-z).")
            return None
        if letter in guessed:
            type_rich("You already tried that letter.")
            return None

        guessed.append(letter) #add guess to the list

        if letter in current_word:  # reveal all occurrences of this letter
            for i, ch in enumerate(current_word):
                if ch == letter:
                    revealed[i] = letter
            type_rich("✅ Correct.")
            print_status()
            if "_" not in revealed: #if no underscores left - word completed
                finish_success()
        else: #wrong guess
            attempts_left -= 1
            type_rich("❌ Not present.")
            print_status()
            if attempts_left <= 0:  #if no attempts left - left and eject
                return fail_and_eject()
        return None

    def handle_solve(word):
        nonlocal attempts_left
        if state["flags"]["projectroom3_solved"]:
            type_rich("✅ Already solved.")
            return None
        if not puzzle_active:
            type_rich("No active puzzle. Use 'start challenge' first.")
            return None

        guess = word.strip().lower()
        if guess == current_word:  # correct solution
            for i, ch in enumerate(current_word):
                revealed[i] = ch
            finish_success()
            return None
        else:  # wrong solution
            attempts_left -= 1
            type_rich("❌ Wrong word.")
            print_status()
            if attempts_left <= 0:
                return fail_and_eject()
        return None

    def handle_take(what): #allow player to take reward after solving puzzle
        name = what.strip().lower()
        if name not in [REWARD_ITEM.lower(), ITEM_4]: #onnly allow specific names for the hard disk
            print(f"❌ There is no '{what}' to take here.")
            return
        if not state["flags"]["projectroom3_solved"]: #if the console puzzle is not solved yet, they cannot take the reward
            type_rich("The console is still locked. Nothing to take yet.")
            return
        if state["flags"]["projectroom3_reward_taken"]: #if the reward was already taken, prevent duplication
            type_rich("You already took the reward from this room.")
            return
        state["flags"]["projectroom3_reward_taken"] = True
        if REWARD_ITEM not in state["inventory"]:
            state["inventory"].append(REWARD_ITEM)
        print(f"🧷 Taken: {REWARD_ITEM}.")

    def handle_go(dest): #handle leaving this room back to corridor
        if dest in [ROOM1, "back"]:
            type_rich(f"You leave Project Room 3 and return to the {ROOM1}.")
            state["previous_room"] = ROOM4
            return ROOM1
        type_rich(f"❌ You can't go to '{dest}' from here.")
        return None

    # ---------------- main input loop ----------------
    while True: #this keeps running until the player leaves the room, while it is inside the room
        command = input("\n> ").strip()

        if command == "look around": #show the room description again
            show_room()

        elif command == "?": #show available commands
            show_help()

        elif command == "display status":
            display_status(state)

        elif command == "start challenge": #begin the hangman puzzlr
            start_challenge()

        elif command.startswith("guess "): #guess a single letter
            result = handle_guess(command[6:])
            if result:
                return result

        elif command.startswith("solve "): #try to solve the whole word
            result = handle_solve(command[6:])
            if result:
                return result

        elif command.startswith("take "):
            handle_take(command[5:])

        elif command.startswith("go "):
            result = handle_go(command[3:].strip().lower())
            if result:
                return result

        elif command in [f"go {ROOM1}", "go back", "back"]:
            result = handle_go(ROOM1)
            if result:
                return result

        elif command == "pause":
            type_rich("⏸️ Game paused. Your progress has been saved.")
            try:
                save_state(state)
            finally:
                sys.exit()

        elif command == "quit":
            type_rich("👋 You close your notebook and leave the project behind. Progress not saved.")
            try:
                clear_state()
                reset_state(state)
            finally:
                sys.exit()

        else:
            type_rich("❓ Unknown command. Type '?' for help.")


if __name__ == "__main__":
    state = get_default_state()
    state["inventory"].append(ITEM_3)
    enter_projectroom3(state)
