# -----------------------------------------------------------------------------
# File: studylandscape.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------

import sys
from .utils import chooseNextRoom

def enterStudyLandscape(state):
    approach_destinations = {
        "lab2003": "You approach the massive door. The label says 'LAB2003'. Something important must be inside.",
        "computer": "You see an old but still working computer. Maybe there’s something useful on it.",
        "sample1": "On the table lies a project sample. It looks like an unfinished coursework.",
        "sample2": "This is another sample, but with a nice cover page.",
        "aid_kits": "There’s a first aid kit in the corner. You never know when it might come in handy."
    }

    print("\n🛋️ You step into the study landscape.")
    print("Soft chairs and tables to work and chat with fellow students and a quiet hum of a coffee machine.")
    print("It feels like a place to work but also to pause and catch your breath.")

    # --- Command handlers ---

    def handle_look():
        """Describe the lobby and show exits."""
        print("\nYou take a slow look around.")
        print("There are a few posters on the wall about upcoming student events.")
        print("A group of students is sitting in the corner gazing at a laptop.")
        print("- Possible exit: corridor")
        print("- Your current inventory:", state["inventory"])
        print("You notice several things you could approach:", ", ".join(approach_destinations.keys()))

    def handle_approach(target):
        """Handle approaching objects/areas."""
        key = target.lower()
        if key in approach_destinations:
            print(f"\n👉 {approach_destinations[key]}")
        else:
            print(f"You can't approach '{target}'. Try: {', '.join(approach_destinations.keys())}")

    def handle_help():
        """Show help message with available commands."""
        print("\nAvailable commands:")
        print("- look around         : See what’s in the lobby.")
        print("- approach <thing>    : Inspect an object or area (examples: lab2003, computer).")
        print("- go corridor / back  : Return to the main corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game.")

    def handle_go(destination):
        """Handle movement to another room."""
        if destination in ["corridor", "back"]:
            print("You leave the study landscape and head back into the corridor.")
            state["previous_room"] = "studylandscape"
            return "corridor"
        else:
            print(f"You can't go to '{destination}' from here.")
            return None

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

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command == "quit":
            print("👋 You sit back in the softest chair, close your eyes, and exit the adventure. Game over.")
            sys.exit()

        else:
            print("❓ Unknown command. Type '?' to see available commands.")
