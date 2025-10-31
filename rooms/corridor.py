# -----------------------------------------------------------------------------
# File: corridor.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------
ENCOUNTER_CHANCE_BASE = 0.75 # There is a %75 chance an encounter occurs

import sys, random

from rooms import texts
from rooms.texts import print_minimap
from .utils import clearScreen, handle_help_generic, display_status, take_damage
from persistence import save_state, clear_state, reset_state
from .constants import ITEM_1, ROOM1, ROOM2, ROOM3, ROOM4, ROOM5


def generate_quadratic_inequality(state):

    def has_solution(sign, delta, a): # This is for checking if the equation generated has a solution

        if sign == ">":
            if a > 0:
                return True  # Upward parabola is positive somewhere
            else:  # a < 0
                return delta > 0  # Solution exists only if parabola crosses x-axis
        elif sign == "<":
            if a < 0:
                return True  # Downward parabola is negative somewhere
            else:  # a > 0
                return delta > 0  # Solution exists only if parabola crosses x-axis
        return None

    def generate_function():
        a = 0
        b = 0
        c = 0
        sign_function = ""

        while True:
            a = random.randint(-10, 10)
            if a == 0:
                continue
            b = random.randint(-20, 20)
            if b == 0:
                continue
            c = random.randint(-50, 50)
            if c == 0:
                continue

            sign_function = ""
            if c > 0:
                sign_function= "<"
            else:
                sign_function = ">"

            delta_function = b ** 2 - 4 * a * c

            if has_solution(sign_function, delta_function, a): # If generated equation has no solution, re-generate the equation
                break

        texts.type_rich(raw_text=f"{a}x² + {b}x + {c} {sign_function} 0", dialog=True, delay=0.12)

        return lambda x: eval(f"{a}*x**2 + {b}*x + {c} {sign_function} 0")

    def handle_help():
        handle_help_generic(ROOM1, specifics={"answer <number>" : "Attempt to solve the math question."})

    def handle_answer(answer_given):
        try:
            answer_given = int(answer_given)
        except ValueError:
            return False
        if check(answer_given):
            texts.type_rich("✅ Correct!")
            return True
        else:
            texts.type_rich("❌ Incorrect.")
            return False

    check = generate_function() # This will return a boolean

    while True:
        command = input("\n> ").strip().lower()

        if command == "?":
            handle_help()
            print_minimap(state)

        elif command == "display status":
            display_status(state)

        elif command.startswith("answer "):
            answer = command[7:].strip()
            result = handle_answer(answer)
            return result

        elif command == "pause":
            texts.type_rich("⏸️ Game paused. Your progress has been saved.")
            try:
                save_state(state)
            finally:
                sys.exit()

        elif command == "quit":
            texts.type_rich("👋 You drop your backpack, leave the maze behind, and step back into the real world. Progress not saved.")
            try:
                clear_state()
                reset_state(state)
            finally:
                sys.exit()

        else:
            texts.type_rich("❓ Unknown command. Type '?' to see available commands.")

def enter_corridor(state):
    state["visited"][ROOM1] = True
    if state["challenge-completed"][ROOM1]:
        texts.CORRIDOR_EMPTY()
    elif state["corridor-encounters"] < 3:
        texts.CORRIDOR_TEXT_VISITED_0()

    # --- List of accessible rooms from here ---
    available_rooms = [ROOM2, ROOM3, ROOM4, ROOM5]
    # --- Calculate encounter chance ---
    turn_roll = random.random()

    if turn_roll < ENCOUNTER_CHANCE_BASE and not state["challenge-completed"][ROOM1]:
        texts.CORRIDOR_TEXT_ENCOUNTER_0()
        texts.CORRIDOR_TEXT_ENCOUNTER_1()
        texts.CORRIDOR_TEXT_ENCOUNTER_2()
        result = generate_quadratic_inequality(state)
        if result:
            texts.CORRIDOR_TEXT_PROBLEM_SOLVED_0()
            state["corridor-encounters"] -= 1
            if state["corridor-encounters"] == 0: # If all encounters are completed, give the item
                texts.CORRIDOR_TEXT_REVEAL_ITEM()
                state["challenge-completed"][ROOM1] = True
        else:
            texts.CORRIDOR_TEXT_PROBLEM_FAILED_0()
            take_damage(state)
            texts.CORRIDOR_TEXT_PROBLEM_FAILED_1()
    else:
        texts.CORRIDOR_TEXT_NO_ENCOUNTER()

    # --- Command handlers ---

    def handle_look():
        """Describe the corridor and show where the player can go."""
        texts.type_rich("You take a look around...", dialog=True)
        texts.type_rich("The corridor stretches out in both directions, illuminated by a dim bluish glow from panels hidden in the ceiling.")
        texts.type_rich("Most of the doors are covered with dark, frosted glass — you can barely make out faint shapes moving behind some of them.")
        texts.type_rich("Occasional static hums from broken lights, and somewhere distant you hear a mechanical hiss.")
        texts.type_rich("Posters on the walls flicker faintly:")
        texts.type_rich("[yellow]  [1] 'SECURITY PROTOCOL OMEGA — AUTHORIZED PERSONNEL ONLY.'[/yellow]")
        texts.type_rich("[magenta]  [2] 'Your mind is your access key.'[/magenta]")
        texts.type_rich("[cyan]  [3] 'Emergency evacuation: FOLLOW THE BLUE LIGHT.'[/cyan]")
        texts.type_rich("")
        texts.type_rich(f"[green]Possible doors: {', '.join(available_rooms)}[/green]")
        texts.type_rich(f"[blue]Your current inventory: {state['inventory']}[/blue]")
        texts.type_rich(f"[red]Your current health: {state['health']}[/red]")
    
    def handle_help():
        if state["challenge-completed"][ROOM1] and ITEM_1 not in state["inventory"]:
            handle_help_generic(room_name=ROOM1, specifics={f"take {ITEM_1}": "Pick up the manual once it's revealed"})
        else:
            handle_help_generic(room_name=ROOM1)

    def handle_take(item_input):
        if item_input == ITEM_1:
            if not state["challenge-completed"][ROOM1]:
                texts.type_rich(f"❌ There's no {ITEM_1} visible yet. Visit again to see more challenges")
            elif ITEM_1 in state["inventory"]:
                texts.type_rich(f"You already have the {ITEM_1} in your backpack.")
            else:
                texts.type_rich("You take it and tuck it safely into your backpack.", dialog=True)
                state["inventory"].append(ITEM_1)
        else:
            texts.type_rich(f"There is no '{item_input}' here to take.")

    def handle_go(room_name):
        """Move to a listed room."""
        room_name = room_name.lower()
        if room_name in available_rooms:
            clearScreen()
            texts.type_rich(f"You walk toward the door to {room_name}.", dialog=True)
            state["previous_room"] = ROOM1
            return room_name
        else:
            texts.type_rich(f"❌ '{room_name}' is not a valid exit. Use 'look around' to see available options.")
            return None

    # --- Main corridor command loop ---
    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            handle_look()

        elif command == "?":
            handle_help()

        elif command == "display status":
            display_status(state)

        elif command.startswith("take "):
            item = command[5:].strip()
            handle_take(item)

        elif command.startswith("go "):
            room = command[3:].strip()
            result = handle_go(room)
            print_minimap(state)
            if result:
                return result

        elif command == "pause":
            texts.type_rich("⏸️ Game paused. Your progress has been saved.")
            try:
                save_state(state)
            finally:
                sys.exit()

        elif command == "quit":
            texts.type_rich("👋 You leave the school and the adventure comes to an end. Progress not saved.")
            try:
                clear_state()
                reset_state(state)
            finally:
                sys.exit()

        else:
            texts.type_rich("❓ Unknown command. Type '?' to see available commands.", dialog=True)
