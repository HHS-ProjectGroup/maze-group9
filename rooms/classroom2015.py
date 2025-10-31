# -----------------------------------------------------------------------------
# File: classroom2015.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: Sept 2025
# -----------------------------------------------------------------------------

import sys
from rooms.texts import print_minimap
from persistence import save_state, clear_state, reset_state
from rooms import texts
from rooms.utils import display_status, handle_help_generic
from .constants import ITEM_2, ITEM_3, ROOM1, ROOM3


def enter_classroom2015(state):
    # --- persistent state for conversation only ---
    room_states = state.setdefault("room_states", {})
    room = room_states.setdefault(ROOM3, {
        "stage": 0,        # 0 = not started, 1..N = questions
        "missteps": 0,
        "conversation_active": False,
    })

    texts.c2015_WELCOME_0()

    # ---------------- Conversation stages (MCQ) ----------------
    QUESTIONS = {
        1: {
            "prompt": '🤖 "IDENT—IDENT… threat proximity…" The cyborg twitches.',
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
                "a": f"Polite: 'I need a {ITEM_3} to continue, please.'",
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
        handle_help_generic(ROOM3, specifics={
            "approach cyborg": f"Begin or continue the conversation (requires {ITEM_2}).",
            "choose <a|b|c|d>": "Pick an answer",
            "search large desk": "Inspect the large desk",
            f"take {ITEM_3}": "Pick up the keycard (once visible).",
            "check inventory": "See what you are carrying.",
        })


    def handle_check_inventory():
        if state["inventory"]:
            texts.type_rich("🎒 You open your backpack. Inside you find:")
            for item in state["inventory"]:
                texts.type_rich(f"- {item}")
        else:
            texts.type_rich("\n🎒 Your backpack is empty.")

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
        if not has_item(ITEM_3):
            texts.type_rich(f"🤖 The cyborg opens a panel and places a {ITEM_3} on the large desk.")
        else:
            texts.type_rich("🤖 'Resource already provided.'")

    def show_question():
        if room["stage"] in QUESTIONS:
            q = QUESTIONS[room["stage"]]
            texts.type_rich(f"{q['prompt']}", dialog=True)
            for key, text in q["options"].items():
                texts.type_rich(f"  {key.upper()}) {text}", dialog=True)
        elif room["stage"] == 4:
            texts.type_rich("🤖 He gestures to the desk:")
            texts.type_rich("'We are done here.'", dialog=True)

    def start_conversation():
        if not has_item(ITEM_2):
            texts.c2015_APPROACH(has_item=False)
            return
        else:
            texts.c2015_APPROACH(has_item=True)
            room["conversation_active"] = True
            room["stage"] = 1
            state["score"] += 30
            show_question()


    def handle_choose(choice: str):
        choice = choice.strip().lower()
        if choice not in ["a", "b", "c", "d"]:
            texts.type_rich("❌ Invalid choice. Use A, B, C, or D.")
            return
        if room["stage"] not in QUESTIONS:
            texts.type_rich("There is no active question.")
            return
        q = QUESTIONS[room["stage"]]
        if choice == q["correct"]:
            texts.type_rich(f"\n✅ {q['success']}")
            room["stage"] += 1
            state["score"] += 100

            if room["stage"] == 4 and not has_item(ITEM_3):
                # grant keycard by placing it on desk
                state["score"] += 40
                place_keycard_on_desk()
        else:
            texts.type_rich("\n❌ Wrong answer. The cyborg stiffens.")
            state["score"] -= 50
            room["missteps"] += 1
            if room["missteps"] >= 3:
                state["score"] -= 100
                texts.type_rich("🚨 The cyborg’s optics flash red. 'Clear the area.'")
                room["stage"] = 1
                room["missteps"] = 0
                room["conversation_active"] = False
                return ROOM1
            else:
                show_question()

    # ---------------- Command loop ----------------
    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            texts.c2015_LOOK_AROUND()
            state["score"] += 10
            if not has_item(ITEM_3) and room["stage"] >= 4:
                texts.type_rich(f"On the desk lies a {ITEM_3}.")
            texts.type_rich(f"- Possible exits: {ROOM1}")
            texts.type_rich(f"- Your inventory: {state["inventory"]}", )

        elif command == "approach cyborg":
            start_conversation()

        elif command.startswith("choose "):
            result = handle_choose(command[7:].strip())
            if result:
                return result
            else:
                show_question()

        elif command in ["a", "b", "c", "d"]:
            result = handle_choose(command)
            if result:
                return result

        elif command == "search large desk":
            if not has_item(ITEM_3) and room["stage"] >= 4:
                texts.type_rich(f"On a pile of holo-slates rests a {ITEM_3}. You can take it.")
            else:
                texts.type_rich("The desk has papers and cables, but nothing special.")

        elif command.startswith("take "):
            item = command[5:].strip().lower()
            if item in [ITEM_3, "keycard"] and not has_item(ITEM_3) and room["stage"] >= 4:
                texts.type_rich(f"🔑 You take the {ITEM_3} and put it in your backpack.")
                state["inventory"].append(ITEM_3)
                state["score"] += 200
            else:
                texts.type_rich(f"There is no '{item}' here to take.")

        elif command == "check inventory":
            handle_check_inventory()

        elif command.startswith("go "):
            dest = command[3:].strip()
            if dest in [ROOM1, "back"]:
                texts.type_rich(f"🚪 You leave the classroom and return to the {ROOM1}.")
                print_minimap(state)
                return ROOM1
            else:
                texts.type_rich(f"❌ You can’t go to '{dest}' from here.")

        elif command == "?":
            handle_help()
            print_minimap(state)

        elif command == "display status":
            display_status(state)

        elif command == "pause":
            texts.type_rich("⏸️ Game paused. Your progress has been saved.")
            try:
                save_state(state)
            finally:
                sys.exit()

        elif command == "quit":
            texts.type_rich("👋 You drop your backpack and exit the maze. Progress not saved.")
            try:
                clear_state()
                reset_state(state)
            finally:
                sys.exit()

        else:
            texts.type_rich("❓ Unknown command. Type '?' to see available commands.")
