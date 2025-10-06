# -----------------------------------------------------------------------------
# File: studylandscape.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------
import sys

#Bianca's room item. It is needed in order to get the access to the StudyLandscape
REWARD_ITEM = "Hard Disk"

#the list of all the rooms
rooms = ["Classroom2015", "Corridor", "FrontDeskOffice", "Lab03", "Lab01", "ProjectRoom3", "StudyLandscape"]

#the list of room which are accessible from the StudyLandcapeRoom
available_rooms = ["corridor", "Lab01", "Lab03"]
#did you approach a computer
approach_computer = False

# Decrypted word + encryption shift (CEASER encryption)
word = "cardboard"
shift = 4

approach_destinations = {
    "Lab03": "You approach the massive door. The label says 'LAB03'. Something important must be inside.",
    "Lab01": "You see an old but still working computer. Maybe there’s something useful on it.",
    "corridor": "On the table lies  a project sample. It looks like an unfinished coursework.",
    "computer": "This is another sample, but with a nice cover page.",
    "aid_kits": "There’s a first aid kit in the corner. You never know when it might come in handy."
}

#the enter script
def enterStudyLandscape(state):

    print("\n🛋️ You step into the study landscape.")
    print("Soft chairs and tables to work and chat with fellow students and a quiet hum of a coffee machine.")
    print("It feels like a place to work but also to pause and catch your breath.")

    if REWARD_ITEM in state["inventory"]:
        print("Hard Disk is in your inventory")
        state["current_room"] = "StudyLandscape"
    else:
        print("Access denied")

    # --- Command handlers ---
#story-telling script
    def handle_look():
        """Describe the lobby and show exits."""
        print("\nYou take a slow look around.")
        print("There are a few posters on the wall about upcoming student events.")
        print("A group of students is sitting in the corner gazing at a laptop.")
        print("- Possible exit: corridor")
        print("- Your current inventory:", state["inventory"])
        print("You notice several things you could approach:", ", ".join(approach_destinations.keys()))

    # Decryption challenge. Ceaser encryption
    def decrypt(text, shift):
        #alphabet
        print("A B C D E F\nG H I J K L\nM N O P Q R\nS T U V W X\nY Z")
        print(f"shift: {shift} direction: right")

        #encrypted word
        encrypted = ""

        for char in text:
            if char.isalpha():
                if char.islower():
                    encrypted += chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
                else:
                    encrypted += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            else:
                encrypted += char
        print(f'\n" Encrypted word is {encrypted}')

        guess = input("Your guess: ").strip().lower()
        if guess == word:
            print("Congratulations! You got it!")
        else:
            print("wrong")

            #User gave wrong answer. Does he want to give a new one?
            def wanna_decrypt_choice():
                wanna_try = input('Do you want to take one more guess? "yes" or "no": ').strip().lower()
                if wanna_try == "yes":
                    decrypt(text, shift)
                elif wanna_try == "no":
                    print("computer is shut down")
                else:
                    print("write yes or no")
                    wanna_decrypt_choice()

            wanna_decrypt_choice()

            #Approach script, story telling + functionality
    def handle_approach(target):

        """Handle approaching objects/areas."""

        matched_key = next((key for key in approach_destinations if key.lower() == target.lower()), None)

        if matched_key:
            print(f"\n👉 {approach_destinations[matched_key]}")

            if matched_key.lower() == "computer":
                global approach_computer
                approach_computer = True

                #Does our player even wants to start decrypting?
                def wanna_play_decrypt_choice():
                    wanna_play_decrypt = input('You are approaching the computer. Type "decrypt" to try, otherwise "no": ').strip().lower()
                    if wanna_play_decrypt == "decrypt" and approach_computer:
                        decrypt(word, shift)
                    elif wanna_play_decrypt == "no":
                        print("computer is shut down")
                    else:
                        print("write decrypt or no")
                        wanna_play_decrypt_choice()

                wanna_play_decrypt_choice()

            elif matched_key.lower() == "lab03":
                 print("Yuo see the massive metal door. You have typ in the secret word, in order to open it")
                 user_secret_word = str(input("Enter your secret word: "))
                 if user_secret_word == word:
                    handle_go("Lab03")
                 elif user_secret_word != word:
                     state["current_room"] = "StudyLandscape"
                     user_secret_word = user_secret_word_fail()
                     if user_secret_word == word:
                         handle_go("Lab03")
                     else:
                         user_secret_word_fail()

        else:
            print(f"You can't approach '{target}'. Try: {', '.join(approach_destinations.keys())}")

            #The list with all the commands
    def handle_help():
        """Show help message with available commands."""
        print("\nAvailable commands:")
        print("- look around         : See what’s in the lobby.")
        print(f"- approach <thing>    : {approach_destinations} ")
        print("- go corridor / back  : Return to the main corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game.")
        print(f"Current room is {state['current_room']}.")

    # Go function, through this function user can go to the other room.
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
                print('This command does not exist. Check "?" out to find appropriate commands.')

    def print_minimap(state):
        state = {"current_room": "enterLab03"}
        current_room = state.get("current_room", "")

        def mark(room_func):
            return "*" if current_room == room_func else " "

        minimap = f"""
    (7) Lab2001 {mark("enterClassroom2015")} ───(6) Lab203 {mark("enterLab01")} ───(5) Lobby {mark("enterLab03")}───(1) Corridor {mark("enterStudyLandscape")}───(2) Front Desk {mark("enterFrontDeskOffice")}
                                              │
                                              │
                                              │
                              ┌───────────────┴───────────────┐
                           (3) Room3 {mark("enterProjectRoom3")}        (4) HDD Room {mark("enterHDDRoom")}
        """.strip("\n")

        print(minimap)

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


''' Code for solo launch'''
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
