# -----------------------------------------------------------------------------
# File: projectroom3.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------
# Testing git

import sys

ENTRY_KEYCARD = "yellow keycard"
REWARD_ITEM   = "Hard Disk"

# Hangman-Lite settings (you can tweak these)
TARGET_WORD   = "protocol"   # keep lowercase
MAX_ATTEMPTS  = 6            # wrong guesses allowed

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
            print("\n🪪 You tap the yellow keycard. The lock turns green and the door slides open.")

    # ---------- room description ----------
    print("\n🧩 You enter Project Room 3.")
    if solved:
        print("The console in the center is calm. Status: UNLOCKED.")
    else:
        print("Long tables are covered in laptops, cables, and half-finished projects.")
        print("Posters of old hackathons line the walls; the room smells faintly of solder and coffee.")
        print("In the center stands a glowing console, its screen flickering with a masked word.")
        print("A cyberteacher avatar materializes: 'Restore the system by guessing the word.'")

    # mark as visited so the door gate won't repeat
    state["visited"]["projectroom3"] = True

    # ---------- per-visit puzzle runtime (resets if you leave/fail) ----------
    attempts_left = MAX_ATTEMPTS
    revealed      = ["_" for _ in TARGET_WORD]
    guessed       = []            # letters tried
    puzzle_active = False         # becomes True after 'start challenge'

    # ---------------- helpers ----------------
    def show_help():
        print("\nCommands:")
        print("- look around                 : Describe the room.")
        print("- start challenge             : Begin/continue the hangman puzzle.")
        print("- guess <letter>              : Guess one letter (a-z).")
        print("- solve <word>                : Attempt the full word.")
        print(f"- take {REWARD_ITEM.lower()}               : Take the reward (after success).")
        print("- go corridor / back          : Leave the room.")
        print("- ?                           : Show this help.")
        print("- quit                        : Quit the game.")

    def show_room():
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

    def word_mask():
        return " ".join(revealed)

    def print_status():
        guessed_str = ", ".join(guessed) if guessed else "-"
        print(f"Word: {word_mask()}   Attempts left: {attempts_left}   Guessed: {guessed_str}")

    def start_challenge():
        nonlocal puzzle_active
        if state["flags"]["projectroom3_solved"]:
            print("✅ The console is already unlocked.")
            return
        if not puzzle_active:
            puzzle_active = True
            print("\n⚙️  The console activates. The cyberteacher says:")
            print("“Guess the hidden word. Use 'guess <letter>' or 'solve <word>'.”")
        print_status()

    def finish_success():
        state["flags"]["projectroom3_solved"] = True
        print("\n🎉 The console flashes green. WORD UNLOCKED.")
        if not state["flags"]["projectroom3_reward_taken"]:
            print(f"🏅 A compartment opens, revealing the {REWARD_ITEM}. Use 'take {REWARD_ITEM.lower()}'.")
        else:
            print("The reward compartment is already empty.")

    def fail_and_eject():
        print("\n🚨 Alarms blare. The console locks and the door slides open.")
        print("The cyberteacher: “Return when you are ready.”")
        return "corridor"

    def handle_guess(letter):
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

        guessed.append(letter)

        if letter in TARGET_WORD:
            for i, ch in enumerate(TARGET_WORD):
                if ch == letter:
                    revealed[i] = letter
            print("✅ Correct.")
            print_status()
            if "_" not in revealed:
                finish_success()
        else:
            attempts_left -= 1
            print("❌ Not present.")
            print_status()
            if attempts_left <= 0:
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
        if guess == TARGET_WORD:
            for i, ch in enumerate(TARGET_WORD):
                revealed[i] = ch
            finish_success()
            return None
        else:
            attempts_left -= 1
            print("❌ Wrong word.")
            print_status()
            if attempts_left <= 0:
                return fail_and_eject()
        return None

    def handle_take(what):
        name = what.strip().lower()
        if name not in [REWARD_ITEM.lower(), "harddisk", "hard disk"]:
            print(f"❌ There is no '{what}' to take here.")
            return
        if not state["flags"]["projectroom3_solved"]:
            print("The console is still locked. Nothing to take yet.")
            return
        if state["flags"]["projectroom3_reward_taken"]:
            print("You already took the reward from this room.")
            return
        state["flags"]["projectroom3_reward_taken"] = True
        if REWARD_ITEM not in state["inventory"]:
            state["inventory"].append(REWARD_ITEM)
        print(f"🧷 Taken: {REWARD_ITEM}.")

    def handle_go(dest):
        if dest in ["corridor", "back"]:
            print("You leave Project Room 3 and return to the corridor.")
            state["previous_room"] = "projectroom3"
            return "corridor"
        print(f"❌ You can't go to '{dest}' from here.")
        return None

    # ---------------- main input loop ----------------
    while True:
        command = input("\n> ").strip()

        if command == "look around":
            show_room()

        elif command == "?":
            show_help()

        elif command == "start challenge":
            start_challenge()

        elif command.startswith("guess "):
            result = handle_guess(command[6:])
            if result:
                return result

        elif command.startswith("solve "):
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

        elif command == "quit":
            print("👋 You close your notebook and leave the project behind. Game over.")
            sys.exit()

        else:
            print("❓ Unknown command. Type '?' for help.")
