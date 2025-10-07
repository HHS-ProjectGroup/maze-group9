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
from persistence import save_state, clear_state, reset_state
from typing import cast

ENTRY_KEYCARD = "yellow keycard"  # item needed to unlock the door
REWARD_ITEM = "Hard Disk"  # reward given after solving

# Hangman-Lite settings
WORDS = [
    "protocol",
    "network",
    "hardware",
    "software",
    "debugger",
    "compiler",
    "variable",
    "function",
    "iterate",
    "package",
    "python",
    "student",
    "teacher",
    "project",
    "console",
]

MAX_ATTEMPTS = 6  # wrong guesses allowed


def enterProjectRoom3(state):
    state.setdefault("visited", {})
    state["visited"].setdefault("projectroom3", False)

    state.setdefault("inventory", [])
    state.setdefault("previous_room", "corridor")

    state.setdefault("flags", {})
    state["flags"].setdefault("projectroom3_solved", False)
    state["flags"].setdefault("projectroom3_reward_taken", False)

    solved = state["flags"]["projectroom3_solved"]
    reward_taken = state["flags"]["projectroom3_reward_taken"]

    # ---------- gate: first-ever entry needs the keycard ----------
    if not state["visited"]["projectroom3"]:
        if ENTRY_KEYCARD not in state["inventory"]:
            print("\n🔒 The door to Project Room 3 blinks red.")
            print("AI voice: 'Access denied. Present Classroom2025 Keycard.'")
            return "corridor"
        else:
            print(
                "\n🪪 You tap the yellow keycard. The lock turns green and the door slides open."
            )

    # ---------- room description ----------
    print("\n🧩 You enter Project Room 3.")
    if solved:
        print("The console in the center is calm. Status: UNLOCKED.")
    else:
        print("Long tables are covered in laptops, cables, and half-finished projects.")
        print(
            "Posters of old hackathons line the walls; the room smells faintly of solder and coffee."
        )
        print(
            "In the center stands a glowing console, its screen flickering with a masked word."
        )
        print(
            "A cyberteacher avatar materializes: 'Restore the system by guessing the word.'"
        )

    # mark as visited so the door gate won't repeat
    state["visited"]["projectroom3"] = True
    current_word = None
    if not state["flags"]["projectroom3_solved"]:
        current_word = random.choice(WORDS)

    # ---------- per-visit puzzle runtime (resets if you leave/fail) ----------
    attempts_left = MAX_ATTEMPTS  # player gets 6 mistakes
    revealed = ["_" for _ in (current_word or "")]  # underscores for the chosen word
    guessed = []  # letters tried
    puzzle_active = False  # becomes True after 'start challenge'

    # ---------------- helpers ----------------
    def show_help():
        print("\nCommands:")
        print("- look around                 : Describe the room.")
        print("- start challenge             : Begin/continue the hangman puzzle.")
        print("- guess <letter>              : Guess one letter (a-z).")
        print("- solve <word>                : Attempt the full word.")
        print(
            f"- take {REWARD_ITEM.lower()}               : Take the reward (after success)."
        )
        print("- go corridor / back          : Leave the room.")
        print("- ?                           : Show this help.")
        print("- pause                        : Save and exit (pause the game).")
        print("- quit                        : Quit without saving.")

    def show_room():  # describe the room again, depends on the progress
        print("\nYou look around:")
        print("- Tables, wires, and a humming console.")
        if state["flags"]["projectroom3_solved"]:
            if not state["flags"]["projectroom3_reward_taken"]:
                print(f"- A slot is open. You can 'take {REWARD_ITEM.lower()}'.")
            else:
                print("- The reward compartment is empty (already claimed).")
        else:
            print("- The console shows a masked word. You can 'start challenge'.")
        print("- Exits: corridor")
        print("- Inventory:", state["inventory"])

    def word_mask():  # return the word display , underscores + revealed letters
        return " ".join(revealed)

    def print_status():  # show the puzzle progress
        guessed_str = ", ".join(guessed) if guessed else "-"
        print(
            f"Word: {word_mask()}   Attempts left: {attempts_left}   Guessed: {guessed_str}"
        )

    def start_challenge():  # start the hangman puzzle
        nonlocal puzzle_active
        if state["flags"]["projectroom3_solved"]:
            print("✅ The console is already unlocked.")
            return
        if not puzzle_active:
            puzzle_active = True
            print("\n⚙️  The console activates. The cyberteacher says:")
            print("“Guess the hidden word. Use 'guess <letter>' or 'solve <word>'.”")
        print_status()

    def finish_success():  # when puzzle is solved correctly
        state["flags"]["projectroom3_solved"] = True
        print("\n🎉 The console flashes green. WORD UNLOCKED.")
        if not state["flags"]["projectroom3_reward_taken"]:
            print(
                f"🏅 A compartment opens, revealing the {REWARD_ITEM}. Use 'take {REWARD_ITEM.lower()}'."
            )
        else:
            print("The reward compartment is already empty.")

    def fail_and_eject():  # if puzzle fails, player is sent out
        print("\n🚨 Alarms blare. The console locks and the door slides open.")
        print("The cyberteacher: “Return when you are ready.”")
        return "corridor"

    def handle_guess(letter):  # process a single letter guess in hangman
        nonlocal attempts_left
        if state["flags"]["projectroom3_solved"]:
            print("✅ Already solved.")
            return None
        if not puzzle_active:
            print("No active puzzle. Use 'start challenge' first.")
            return None

        letter = letter.strip().lower()
        if len(letter) != 1 or not letter.isalpha():
            print("Please guess a single letter (a-z).")
            return None
        if letter in guessed:
            print("You already tried that letter.")
            return None

        guessed.append(letter)  # add guess to the list

        if letter in current_word:  # reveal all occurrences of this letter
            for i, ch in enumerate(cast(str, current_word)):
                if ch == letter:
                    revealed[i] = letter
                    print("✅ Correct.")
                print_status()
                if "_" not in revealed:  # if no underscores left - word completed
                    finish_success()
        else:  # wrong guess
            attempts_left -= 1
            print("❌ Not present.")
            print_status()
            if attempts_left <= 0:  # if no attempts left - left and eject
                return fail_and_eject()
        return None

    def handle_solve(word):
        nonlocal attempts_left
        if state["flags"]["projectroom3_solved"]:
            print("✅ Already solved.")
            return None
        if not puzzle_active:
            print("No active puzzle. Use 'start challenge' first.")
            return None

        guess = word.strip().lower()
        if guess == current_word:  # correct solution
            for i, ch in enumerate(cast(str, current_word)):
                revealed[i] = ch
                finish_success()
                return None
        else:  # wrong solution
            attempts_left -= 1
            print("❌ Wrong word.")
            print_status()
            if attempts_left <= 0:
                return fail_and_eject()
        return None

    def handle_take(what):  # allow player to take reward after solving puzzle
        name = what.strip().lower()
        if name not in [
            REWARD_ITEM.lower(),
            "harddisk",
            "hard disk",
        ]:  # onnly allow specific names for the hard disk
            print(f"❌ There is no '{what}' to take here.")
            return
        if not state["flags"][
            "projectroom3_solved"
        ]:  # if the console puzzle is not solved yet, they cannot take the reward
            print("The console is still locked. Nothing to take yet.")
            return
        if state["flags"][
            "projectroom3_reward_taken"
        ]:  # if the reward was already taken, prevent duplication
            print("You already took the reward from this room.")
            return
        state["flags"]["projectroom3_reward_taken"] = True
        if REWARD_ITEM not in state["inventory"]:
            state["inventory"].append(REWARD_ITEM)
        print(f"🧷 Taken: {REWARD_ITEM}.")

    def handle_go(dest):  # handle leaving this room back to corridor
        if dest in ["corridor", "back"]:
            print("You leave Project Room 3 and return to the corridor.")
            state["previous_room"] = "projectroom3"
            return "corridor"
        print(f"❌ You can't go to '{dest}' from here.")
        return None

    # ---------------- main input loop ----------------
    while True:  # this keeps running until the player leaves the room, while it is inside the room
        command = input("\n> ").strip()

        if command == "look around":  # show the room description again
            show_room()

        elif command == "?":  # show available commands
            show_help()

        elif command == "start challenge":  # begin the hangman puzzlr
            start_challenge()

        elif command.startswith("guess "):  # guess a single letter
            result = handle_guess(command[6:])
            if result:
                return result

        elif command.startswith("solve "):  # try to solve the whole word
            result = handle_solve(command[6:])
            if result:
                return result

        elif command.startswith("take "):
            handle_take(command[5:])

        elif command.startswith("go "):
            result = handle_go(command[3:].strip().lower())
            if result:
                return result

        elif command in ["go corridor", "go back", "back"]:
            result = handle_go("corridor")
            if result:
                return result

        elif command == "pause":
            print("⏸️ Game paused. Your progress has been saved.")
            try:
                save_state(state)
            finally:
                sys.exit()

        elif command == "quit":
            print(
                "👋 You close your notebook and leave the project behind. Progress not saved."
            )
            try:
                clear_state()
                reset_state(state)
            finally:
                sys.exit()

        else:
            print("❓ Unknown command. Type '?' for help.")
