# -----------------------------------------------------------------------------
# File: classroom2015.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: Sept 2025
# -----------------------------------------------------------------------------

import sys
from persistence import save_state, clear_state, reset_state
from rooms.utils import handle_display_status, display_status


def enterClassroom2015(state):
    # --- persistent state for conversation only ---
    room_states = state.setdefault("room_states", {})
    room = room_states.setdefault("classroom2015", {
        "stage": 0,        # 0 = not started, 1..N = questions
        "missteps": 0,
        "conversation_active": False,
    })

    print("\n🏫 You step into Classroom 2.015.")
    print("Holographic desks shimmer beside ergonomic chairs. A larger desk stands at the front,")
    print("and wide windows flood the room with light. In the corner, a janitor cyborg sits rigidly.")

    # ---------------- Conversation stages (MCQ) ----------------
    QUESTIONS = {
        1: {
            "prompt": '🤖 "IDENT—IDENT… threat proximity…" The cyborg twitches.\nHow do you respond?',
            "options": {
                "a": "Keep distance, hands visible: 'It’s okay. I mean no harm.'",
                "b": "Bark: 'Stand down and obey!'",
                "c": "Reach for his panel: 'Let me fix you…'",
                "d": "Demand: 'Give me the keycard now!'",
            },
            "correct": "a",
            "success": "He relaxes a fraction. '…non-hostile posture detected.'",
        },
        2: {
            "prompt": '🤖 "Context check… role?"',
            "options": {
                "a": "Casual: 'Just passing through.'",
                "b": "Supportive: 'I’m a student. You were the janitor here.'",
                "c": "Technical: 'I can connect you to the network.'",
                "d": "Dismissive: 'Doesn’t matter. Move.'",
            },
            "correct": "b",
            "success": 'He nods. "Janitorial model. Never connected to the network."',
        },
        3: {
            "prompt": '🤖 "Purpose of interaction?"',
            "options": {
                "a": "Polite: 'I need a yellow keycard to continue, please.'",
                "b": "Vague: 'Stuff. Whatever you’ve got.'",
                "c": "Aggressive: 'Give it now or else.'",
                "d": "Techy: 'Let me override your safeties.'",
            },
            "correct": "a",
            "success": 'He considers… "Purpose valid. Providing access."',
        },
    }

    # ---------------- Helpers ----------------

    def handle_help():
        print("\nAvailable commands:")
        print("- look around           : Examine the room.")
        print("- approach cyborg       : Begin or continue the conversation (requires battery).")
        print("- talk                  : Re-show the current question.")
        print("- choose <a|b|c|d>      : Pick an answer.")
        print("- search large desk     : Inspect the large desk.")
        print("- take yellow keycard   : Pick up the keycard (once visible).")
        print("- check inventory       : See what you are carrying.")
        print("- go corridor/back/leave: Exit the room.")
        print("- display status        : Show your inventory, location, and visited rooms.")
        print("- pause                 : Save and exit (pause the game).")
        print("- quit                  : Quit without saving.")

    def handle_check_inventory():
        if state["inventory"]:
            print("\n🎒 You open your backpack. Inside you find:")
            for item in state["inventory"]:
                print(f"- {item}")
        else:
            print("\n🎒 Your backpack is empty.")

    def has_item(name: str) -> bool:
        """Check if an item is in inventory (case-insensitive)."""
        return any(it.lower() == name.lower() for it in state["inventory"])

    def remove_item(name: str):
        """Remove an item from inventory (case-insensitive)."""
        for idx, it in enumerate(state["inventory"]):
            if it.lower() == name.lower():
                state["inventory"].pop(idx)
                return True
        return False

    def place_keycard_on_desk():
        if not has_item("yellow keycard"):
            print("\n🤖 The cyborg opens a panel and places a **yellow keycard** on the large desk.")
        else:
            print("🤖 'Resource already provided.'")

    def show_question():
        if room["stage"] in QUESTIONS:
            q = QUESTIONS[room["stage"]]
            print(f"\n{q['prompt']}")
            for key, text in q["options"].items():
                print(f"  {key.upper()}) {text}")
        elif room["stage"] == 4:
            print("🤖 He gestures to the desk. 'We are done here.'")

    def start_conversation():
        if not has_item("battery"):
            print('\n🤖 "I need more energy." (You need a battery in your inventory to talk to him.)')
            return
        if not room["conversation_active"]:
            room["conversation_active"] = True
            room["stage"] = 1
            print("\nYou carefully approach the cyborg…")
        show_question()

    def handle_choose(choice: str):
        choice = choice.strip().lower()
        if choice not in ["a", "b", "c", "d"]:
            print("❌ Invalid choice. Use A, B, C, or D.")
            return
        if room["stage"] not in QUESTIONS:
            print("There is no active question.")
            return
        q = QUESTIONS[room["stage"]]
        if choice == q["correct"]:
            print(f"\n✅ {q['success']}")
            room["stage"] += 1
            if room["stage"] == 4 and not has_item("yellow keycard"):
                # grant keycard by placing it on desk
                place_keycard_on_desk()
        else:
            print("\n❌ Wrong answer. The cyborg stiffens.")
            room["missteps"] += 1
            if room["missteps"] >= 3:
                print("🚨 The cyborg’s optics flash red. 'Clear the area.'")
                room["stage"] = 1
                room["missteps"] = 0
                room["conversation_active"] = False
                return "corridor"
            else:
                show_question()

    # ---------------- Command loop ----------------
    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            print("\nYou see holographic desks, a large desk, big windows, and the cyborg in the corner.")
            if not has_item("yellow keycard") and room["stage"] >= 4:
                print("On the desk lies a **yellow keycard**.")
            print("- Possible exits: corridor")
            print("- Your inventory:", state["inventory"])

        elif command == "approach cyborg":
            start_conversation()

        elif command == "talk":
            show_question()

        elif command.startswith("choose "):
            result = handle_choose(command[7:].strip())
            if result:
                return result

        elif command in ["a", "b", "c", "d"]:
            result = handle_choose(command)
            if result:
                return result

        elif command == "search large desk":
            if not has_item("yellow keycard") and room["stage"] >= 4:
                print("On a pile of holo-slates rests a **yellow keycard**. You can take it.")
            else:
                print("The desk has papers and cables, but nothing special.")

        elif command.startswith("take "):
            item = command[5:].strip().lower()
            if item in ["yellow keycard", "keycard"] and not has_item("yellow keycard") and room["stage"] >= 4:
                print("🔑 You take the yellow keycard and put it in your backpack.")
                state["inventory"].append("yellow keycard")
            else:
                print(f"There is no '{item}' here to take.")

        elif command == "check inventory":
            handle_check_inventory()

        elif command.startswith("go "):
            dest = command[3:].strip()
            if dest in ["corridor", "back", "leave"]:
                print("🚪 You leave the classroom and return to the corridor.")
                return "corridor"
            else:
                print(f"❌ You can’t go to '{dest}' from here.")

        elif command in ["leave", "back"]:
            print("🚪 You leave the classroom and return to the corridor.")
            state["visited"]["classroom2015"] = True
            return "corridor"

        elif command == "?":
            handle_help()

        elif command == "display status":
            display_status(state)

        elif command == "pause":
            print("⏸️ Game paused. Your progress has been saved.")
            try:
                save_state(state)
            finally:
                sys.exit()

        elif command == "quit":
            print("👋 You drop your backpack and exit the maze. Progress not saved.")
            try:
                clear_state()
                reset_state(state)
            finally:
                sys.exit()

        else:
            print("❓ Unknown command. Type '?' to see available commands.")
