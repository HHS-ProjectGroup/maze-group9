# -----------------------------------------------------------------------------
# File: studylandscape.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------

import sys

REWARD_ITEM   = "Hard Disk"
rooms = ["Classroom2015", "Corridor", "FrontDeskOffice", "Lab03", "Lab01", "ProjectRoom3", "StudyLandscape"]

def enterStudyLandscape(state):
    if "Hard Disk" in state["inventory"]:
        print("Hard Disk is in your inventory")
        state["current_room"] = "StudyLandscape"
    else:
        print("Access denied")

    available_rooms = ["corridor", "lab01", "lab03"]

    approach_destinations = {
        "lab03": "You approach the massive door. The label says 'LAB2003'. Something important must be inside.",
        "lab01": "You see an old but still working computer. Maybe there’s something useful on it.",
        "corridor": "On the table lies a project sample. It looks like an unfinished coursework.",
        "computer": "This is another sample, but with a nice cover page.",
        "aid_kits": "There’s a first aid kit in the corner. You never know when it might come in handy."
    }

    print("\n🛋️ You step into the study landscape.")
    print("Soft chairs and tables to work and chat with fellow students and a quiet hum of a coffee machine.")
    print("It feels like a place to work but also to pause and catch your breath.")

    # --- Command handlers ---

    def handle_look():
        """Describe the lobby and show exits."""
        print("\nYou take a slow look around. TEEEEEEEEEEEEEEEEEST")
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
        print(f"- approach <thing>    : {approach_destinations} ")
        print("- go corridor / back  : Return to the main corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game.")
        print(f"Current room is {state['current_room']}.")

    def handle_go(destination):
        """Handle movement to another room."""
        if state["current_room"] == "StudyLandscape":
         if destination in available_rooms:
            print(f"You left StudyLandscape. You step into {destination}")
            state["previous_room"] = "StudyLandscape"
            state["current_room"] = destination
         elif destination in rooms and destination not in available_rooms:
            print(f"You can't access {destination} from {state['current_room']}")

         else:
            'This command does not exist. Check "?" out to find appropriate commands.'

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

''' Code for solo launch
if __name__ == "__main__":
    state = {
        "current_room": "corridor",
        "previous_room": "corridor",
        "visited": {
            "classroom2015": False,
            "projectroom3": False,
            "frontdeskoffice": False,
            "corridor": [False, 3],  # the number of encounters left
        },
        "inventory": ["Hard Disk"],
        "health": 3,
    }
    enterStudyLandscape(state)
'''