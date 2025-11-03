# -----------------------------------------------------------------------------
# File: studylandscape.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------

import sys
from rooms.texts import print_minimap
from persistence import save_state, clear_state, reset_state
from rooms import constants
from rooms.texts import LOBBY_WELCOME, type_rich, glitch_line
from .constants import ITEM_4
from .utils import display_status, handle_help_generic

#Bianca's room item. It is needed in order to get the access to the StudyLandscape
REWARD_ITEM = constants.ITEM_4

# the list of all the rooms
rooms = [
    constants.ROOM1,
    constants.ROOM2,
    constants.ROOM3,
    constants.ROOM4,
    constants.ROOM5,
    constants.ROOM6,
    constants.ROOM7,
]

# the list of room which are accessible from the StudyLandcapeRoom
available_rooms = [constants.ROOM1, constants.ROOM6, constants.ROOM7]

# did you approach a computer
approach_computer = False

# Decrypted word + encryption shift (CEASER encryption)
word = "cardboard"
shift = 4

approach_destinations = {
    "lab03": "You approach the massive door. The label says 'LAB2003'. As you remember from your study, this is a place with the lab desk and server racks.",
    "lab01": "It is a smaller lab. You see a bunch of PCs scattered along the walls. Noone's inside too though.",
    "corridor": "There is nothing new there, except that the oil staines are cleaned. Who could have done it?",
    "computer": "You see an decrypting window opened there. Probably it has something to do with EDEN's or School's firewall",
    "aid_kits": "There’s a first aid kit in the corner. You never know when it might come in handy.",
}


# the enter scrpit
def enter_studylandscape(state):

    if constants.ITEM_4 in state["inventory"]:
        type_rich(f"{constants.ITEM_4} is in your inventory")
        state["current_room"] = constants.ROOM5
        LOBBY_WELCOME()
    else:
        state["current_room"] = constants.ROOM1
        type_rich("Access denied")
        return constants.ROOM1



    # --- Command handlers ---

    # story-telling script
    def handle_look():
        """Describe the lobby and show exits."""
        type_rich("You take a slow look around.")
        type_rich(
            "Soft chairs and worktables fill the open space. Most monitors are in sleep mode."
        )
        type_rich(
            "Glass walls reflect faint emergency lighting. The coffee machine hums, but no one is using it."
        )
        type_rich("- Possible exit: corridor")
        type_rich(f"- Your current inventory: {state['inventory']}")
        type_rich(
            "You notice things you could approach: "
            + ", ".join(approach_destinations.keys())
        )

    # Decryption challenge. Ceaser encryption
    def decrypt(text, shift):
        # alphabet
        type_rich("A B C D E F", dialog=True)
        type_rich("G H I J K L", dialog=True)
        type_rich("M N O P Q R", dialog=True)
        type_rich("S T U V W X", dialog=True)
        type_rich("Y Z", dialog=True)
        type_rich("Hint: shift is left 4")

        # encrypted word
        encrypted = ""

        for char in text:
            if char.isalpha():
                if char.islower():
                    encrypted += chr((ord(char) - ord("a") + shift) % 26 + ord("a"))
                else:
                    encrypted += chr((ord(char) - ord("A") + shift) % 26 + ord("A"))
            else:
                encrypted += char
        type_rich(f'" Encrypted word is {encrypted}', dialog=True)

        guess = input("Your guess: ").strip().lower()
        if guess == word:
            type_rich("Congratulations! You got it!", dialog=True)
            state["score"] += 200
        else:
            type_rich("Wrong", dialog=True)

            # User gave wrong answer. Does he want to give a new one?
            def wanna_decrypt_choice():
                state["score"] -= 50

                wanna_try = (
                    input('Do you want to take one more guess? "yes" or "no": ')
                    .strip()
                    .lower()
                )
                if wanna_try == "yes":
                    decrypt(text, shift)
                elif wanna_try == "no":
                    type_rich("computer is shut down", dialog=True)
                else:
                    type_rich("write yes or no", dialog=True)
                    wanna_decrypt_choice()

            wanna_decrypt_choice()

    # Approach script, story telling + functionality
    def handle_approach(target):
        """Handle approaching objects/areas."""
        key = target.lower()
        if key in approach_destinations:
            type_rich(f"👉 {approach_destinations[key]}")
            if key == "computer":
                global approach_computer
                approach_computer = True

                # Does our player even wants to start decrypting?
                def wanna_play_decrypt_choice():
                    type_rich(
                        'You are approaching the computer. Type "decrypt" to try, otherwise "no": ',
                        dialog=True,
                    )
                    wanna_play_decrypt = input().strip().lower()
                    if wanna_play_decrypt == "decrypt" and approach_computer:
                        decrypt(word, shift)
                    elif wanna_play_decrypt == "no":
                        type_rich("computer is shut down")
                    else:
                        type_rich("write decrypt or no")
                        wanna_play_decrypt_choice()

                wanna_play_decrypt_choice()
        else:
            type_rich(
                f"You can't approach '{target}'. Try: {', '.join(approach_destinations.keys())}"
            )

    # The list with all the commands
    def handle_help():
        """Show help message with available commands."""
        handle_help_generic(
            constants.ROOM5,
            specifics={
                "approach <thing>": f"{', '.join(approach_destinations.keys())}"
            },
        )

    # Go function, through this function user can go to the other room.
    def handle_go(destination: str) -> str:
        """Handle movement to another room."""
        if state["current_room"] == constants.ROOM5:
            if destination in available_rooms:
                type_rich(f"You left StudyLandscape. You step into {destination}")
                state["previous_room"] = constants.ROOM5
                state["current_room"] = destination
                return destination
            elif destination in rooms and destination not in available_rooms:
                type_rich(
                    f"You can't access {destination} from {state['current_room']}"
                )
            else:
                type_rich(
                    'This command does not exist. Check "?" out to find appropriate commands.'
                )
        return ""

    # --- Main command loop ---
    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            handle_look()

        elif command.startswith("approach "):
            target = command.split(" ", 1)[1]
            handle_approach(target)

        elif command == "?":
            handle_help()
            print_minimap(state)

        elif command == "display status":
            display_status(state)

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command == "pause":
            type_rich("⏸️ Game paused. Your progress has been saved.")
            try:
                save_state(state)
            finally:
                sys.exit()

        elif command == "quit":
            type_rich(
                "👋 You sit back in the softest chair, close your eyes, and exit the adventure. Progress not saved."
            )
            try:
                clear_state()
                reset_state(state)
            finally:
                sys.exit()

        else:
            type_rich("❓ Unknown command. Type '?' to see available commands.")


""" Code for solo launch"""
if __name__ == "__main__":
    state = {
        "current_room": constants.ROOM5,
        "previous_room": constants.ROOM1,
        "visited": {
            constants.ROOM3: False,
            constants.ROOM4: False,
            constants.ROOM2: False,
            constants.ROOM1: [False, 3],  # the number of encounters left
        },
        "inventory": [],
        "health": 3,
    }
    enter_studylandscape(state)
