# -----------------------------------------------------------------------------
# File: utils.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------

import os
import sys
from rooms.texts import glitch_line, type_rich


def clearScreen():
    if os.getenv("PYCHARM_HOSTED"):
        print("\n" * 50)  # fallback for PyCharm,
    else:
        os.system("cls" if os.name == "nt" else "clear")


def chooseNextRoom(choices):
    print("\n🔀 Choose a door:")
    for i, room in enumerate(choices, start=1):
        print(f"{i}. {room}")
    choice = input("Enter the number of your choice: ")

    try:
        index = int(choice) - 1
        if 0 <= index < len(choices):
            clearScreen()  # ✅ Clear screen before entering the selected room
            return choices[index]
        else:
            print("Invalid choice.")
            return None
    except ValueError:
        print("Invalid input.")
        return None


def display_status(state):
    """Show the player's current status including inventory, location, and visited rooms."""
    print("\n📊 PLAYER STATUS")
    print(f"- Current location: {state['current_room'].capitalize()}")
    print(f"- Inventory: {state['inventory'] if state['inventory'] else 'Empty'}")
    print(f"- Health: {state['health']} HP")

    visited_rooms = [
        room
        for room, visited in state["visited"].items()
        if room != "corridor" and visited is True
    ]
    if visited_rooms:
        print(f"- Rooms visited: {', '.join(visited_rooms)}")
    else:
        print("- Rooms visited: None yet")


def handle_help_generic(
    room_name: str, specifics: dict[str, str] = {}
):
    """
    Prints help in each room using type_rich() instead of print().
    To add specific commands to your room, pass them as {"command_name": "description", ...}.
    """
    type_rich(f"Available commands for [bold cyan]{room_name}[/bold cyan]:", dialog=True, delay=0.008)
    type_rich(f"- [green]look around[/green]         : See what's in the {room_name} and where you can go.", delay=0.01)
    type_rich("- [green]go <room name>[/green]      : Move to another room. Example: [italic]go classroom2015[/italic]", delay=0.01)
    type_rich("- [green]?[/green]                   : Show this help message.", delay=0.01)
    type_rich("- [green]display status[/green]      : Show your inventory, location, and visited rooms.", delay=0.01)
    type_rich("- [green]pause[/green]               : Save and exit (pause the game).", delay=0.01)
    type_rich("- [green]quit[/green]                : Quit without saving.", delay=0.01)

    if specifics:
        type_rich("\nAdditional commands:")
        for command_name, description in specifics.items():
            pad = " " * max(1, 20 - len(command_name))
            type_rich(
                f"- [green]{command_name.lower()}[/green]{pad}: {description}"
            )

def take_damage(state):
    print("\nYou lost 1 HP.")
    state["health"] -= 1
    if state["health"] == 0:
        print("You died. The game is over.")
        sys.exit()


def beat_game(state):
    type_rich("You beat the game!")
    glitch_line("ヘ( ^o^)ノ＼(^_^ )")
    try:
        # Mark the game as beaten so the leaderboard can be updated in main
        if isinstance(state, dict):
            state["game_beaten"] = True
    finally:
        sys.exit()
