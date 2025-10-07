# -----------------------------------------------------------------------------
# File: corridor.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------
ENCOUNTER_CHANCE_BASE = 0.75 # There is a %75 chance an encounter occurs

import sys, random
from .utils import chooseNextRoom, clearScreen
from .corridorquiz import generate_quadratic_inequality
from .mechanics import take_damage
from persistence import save_state, clear_state, reset_state
from constants import ITEM_1, ROOM1, ROOM2, ROOM3, ROOM4, ROOM5

def enterCorridor(state):
    print("\n🚶 You are standing in the school's main corridor.")
    print("You see a long corridor with many doors and glass walls on both side. Behind these door are rooms, waiting to be explored.")
    print("Dr. Mara Lin said you need to find the manual here.")

    # --- List of accessible rooms from here ---
    available_rooms = [ROOM2, ROOM3, ROOM4, ROOM5]
    # --- Calculate encounter chance ---
    turn_roll = random.random()

    if turn_roll < ENCOUNTER_CHANCE_BASE and not state["visited"][ROOM1][0]:
        print("\nCyborg-teacher finds you were wandering around aimlessly in main corridor and decides to ask you a question.")
        print("He won't let you go until you give an answer.")
        print("He wants you to give an integer that satisfies this inequality:")
        # --- Go to corridorquiz situation, will return a boolean depending on whether player answer correctly ---
        result = generate_quadratic_inequality(state)
        if result:
            print("You managed to avoid his punishment. He goes away and you can go on with the maze.")
            state["visited"][ROOM1][1] -= 1
            if state["visited"][ROOM1][1] == 0: # If all encounters are completed, give the item
                print("\nIt seems that you won't be seeing him again.")
                print("Suddenly you see something on the ground.")
                state["visited"][ROOM1][0] = True
        else:
            print("The cyborg-teacher is really unhappy with your answer. He decides to punish you for that.")
            take_damage(state)
            print("He goes around the corner and disappears. He'll be probably back soon.")
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
        print(f"- look around         : See what's in the {ROOM1} and where you can go.")
        if state["visited"][ROOM1][0] and ITEM_1 not in state["inventory"]:
            print(f"- take {ITEM_1}         : Pick up the {ITEM_1} once it's revealed.")
        print("- go <room name>      : Move to another room. Example: go classroom2015")
        print("- ?                   : Show this help message.")
        print("- pause               : Save and exit (pause the game).")
        print("- quit                : Quit without saving.")

    def handle_take(item):
        if item == ITEM_1:
            if not state["visited"][ROOM1][0]:
                print(f"❌ There's no {ITEM_1} visible yet. Visit again to see more challenges")
            elif ITEM_1 in state["inventory"]:
                print(f"You already have the {ITEM_1} in your backpack.")
            else:
                print("You take it and tuck it safely into your backpack.")
                state["inventory"].append(ITEM_1)
        else:
            print(f"There is no '{item}' here to take.")

    def handle_go(room_name):
        """Move to a listed room."""
        room = room_name.lower()
        if room in available_rooms:
            clearScreen()
            print(f"You walk toward the door to {room}.")
            state["previous_room"] = ROOM1
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

        elif command.startswith("take "):
            item = command[5:].strip()
            handle_take(item)

        elif command.startswith("go "):
            room = command[3:].strip()
            result = handle_go(room)
            if result:
                return result

        elif command == "pause":
            print("⏸️ Game paused. Your progress has been saved.")
            try:
                save_state(state)
            finally:
                sys.exit()

        elif command == "quit":
            print("👋 You leave the school and the adventure comes to an end. Progress not saved.")
            try:
                clear_state()
                reset_state(state)
            finally:
                sys.exit()

        else:
            print("❓ Unknown command. Type '?' to see available commands.")
