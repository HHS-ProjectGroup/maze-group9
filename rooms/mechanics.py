import sys

def take_damage(state):
    print("\nYou lost 1 HP.")
    state["health"] -= 1
    if state["health"] == 0:
        print("You died. The game is over.")
        sys.exit()
