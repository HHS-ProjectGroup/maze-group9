# -----------------------------------------------------------------------------
# File: main.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------
print("main started")
from rooms import enterCorridor, enterStudyLandscape, enterClassroom2015, enterProjectRoom3
print("main imports are resolved")

print("****************************************************************************")
print("*                      Welcome to the School Maze!                         *")
print("*        Your goal is to explore all important rooms in the school.        *")
print("*    You may need to solve challenges to collect items and unlock rooms.   *")
print("*               Once you've visited all rooms, you win!                    *")
print("****************************************************************************")

state = { # this is a dictionary
    "current_room": "corridor",
    "previous_room": "corridor",
    # add the visited rooms here
    "visited": { # this is also a dictionary, i.e nested dict
        "classroom2015": False,
        "projectroom3": False,
        "corridor": False,
    },
    "inventory": [],
    "health": 3
    # In Python, [] defines an empty list. Python does not have an array type
    # A list is an ordered, mutable container that can hold elements of any type(mixed types)
}

while True:
    print("state started")
    current = state["current_room"]

    if current == "corridor":
        state["current_room"] = enterCorridor(state)

    elif current == "studylandscape":
        state["current_room"] = enterStudyLandscape(state)

    elif current == "classroom2015":
        state["current_room"] = enterClassroom2015(state)

    elif current == "projectroom3":
        state["current_room"] = enterProjectRoom3(state)

    else:
        print("Unknown room. Exiting game.")
        break

print("main is run")