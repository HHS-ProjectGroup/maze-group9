# -----------------------------------------------------------------------------
# File: corridor.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------

import sys, random
from .utils import chooseNextRoom, clearScreen
from .corridorquiz import generate_quadratic_inequality


def enterCorridor(state):
    print("\n🚶 You are standing in the school's main corridor.")
    print("You see a long corridor with many doors and glass walls on both side. Behind these door are rooms, waiting to be explored.")

    # --- List of accessible rooms from here ---
    available_rooms = ["classroom2015", "projectroom3", "studylandscape", "frontdeskoffice"]
    # --- Calculate encounter chance ---
    encounter_chance = random.random()

    if encounter_chance < 0.80 and not state["visited"]["corridor"][0]:
        print("\nCyborg-teacher finds you were wandering around aimlessly in main corridor and decides to ask you a question.")
        print("He won't let you go until you give an answer.")
        print("He wants you to give an integer that satisfies this inequality:")
        result = generate_quadratic_inequality(state)
        if result:
            print("You managed to avoid his punishment. He goes away and you can go on with the maze.")
            state["visited"]["corridor"][1] -= 1
            if state["visited"]["corridor"][1] == 0:
                print("It seems that you won't be seeing him again.")
                state["visited"]["corridor"][0] = True
        else:
            print("The cyborg-teacher is really unhappy with your answer. He decides to punish you for that.")
            print("You lost 1 HP.")
            state["health"] -= 1
            if state["health"] == 0:
                print("You died. The game is over.")
                sys.exit()
    else:
        print("\n You don't see any movement in the corridor.")

    # --- Command handlers ---

    def handle_look():
        """Describe the corridor and show where the player can go."""
        print("\nYou take a look around.")
        print("Everything looks so futuristic. There are strange electronics everywhere. You see several labeled doors.")
        print(f"- Possible doors: {', '.join(available_rooms)}")
        print(f"- Your current inventory: {state["inventory"]}")
        print(f"- Your current health: {state["health"]}")

    def handle_help():
        """List available commands and explain navigation."""
        print("\nAvailable commands:")
        print("- look around         : See what's in the corridor and where you can go.")
        print("- go <room name>      : Move to another room. Example: go classroom2015")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game.")

    def handle_go(room_name):
        """Move to a listed room."""
        room = room_name.lower()
        if room in available_rooms:
            clearScreen()
            print(f"You walk toward the door to {room}.")
            state["previous_room"] = "corridor"
            return room
        else:
            print(f"❌ '{room_name}' is not a valid exit. Use 'look around' to see available options.")
            return None

    # --- Main corridor command loop ---
    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            handle_look()

        elif command == "?":
            handle_help()

        elif command.startswith("go "):
            room = command[3:].strip()
            result = handle_go(room)
            if result:
                return result

        elif command == "quit":
            print("👋 You leave the school and the adventure comes to an end. Game over.")
            sys.exit()

        else:
            print("❓ Unknown command. Type '?' to see available commands.")
