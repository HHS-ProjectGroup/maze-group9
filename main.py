from rooms import (
    enterClassroom2015,
    enterCorridor,
    enterFrontDeskOffice,
    enterLab03,
    enterLab01,
    enterProjectRoom3,
    enterStudyLandscape,

)


state = {
    "current_room": "corridor",
    "previous_room": "corridor",
    "visited": {
        "classroom2015": False,
        "projectroom3": False,
        "frontdeskoffice": False,
        "corridor": [False, 3],  # the number of encounters left
    },
    "inventory": [],
    "health": 3,
}


def main(state):
    print(
        "****************************************************************************"
    )
    print(
        "*                      Welcome to the School Maze!                         *"
    )
    print(
        "*        Your goal is to explore all important rooms in the school.        *"
    )
    print(
        "*    You may need to solve challenges to collect items and unlock rooms.   *"
    )
    print(
        "*               Once you've visited all rooms, you win!                    *"
    )
    print(
        "****************************************************************************"
    )

    while True:
        current = state["current_room"]

        # Selim
        if current == "corridor":
            state["current_room"] = enterCorridor(state)

        # Alex
        elif current == "studylandscape":
            state["current_room"] = enterStudyLandscape(state)

        # Gleb
        elif current == "lab03":
            state["current_room"] = enterLab03(state)

        # Arda
        elif current == "frontdeskoffice":
            state["current_room"] = enterFrontDeskOffice(state)

        # Sil
        elif current == "classroom2015":
            state["current_room"] = enterClassroom2015(state)

        # Bianca
        elif current == "projectroom3":
            state["current_room"] = enterProjectRoom3(state)

        elif current == "lab01":
            state["current_room"] = enterLab01(state)

        else:
            print("Unknown room. Exiting game.")
            break


if __name__ == "__main__":
    main(state)
