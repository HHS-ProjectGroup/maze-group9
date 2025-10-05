import random
import sys
from persistence import save_state, clear_state, reset_state


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

        print(f"{a}x² + {b}x + {c} {sign_function} 0")

        return lambda x: eval(f"{a}*x**2 + {b}*x + {c} {sign_function} 0")

    def handle_help():
        print("\nAvailable commands:")
        print("- answer <number>     : Attempt to solve the math question.")
        print("- ?                   : Show this help message.")
        print("- pause               : Save and exit (pause the game).")
        print("- quit                : Quit without saving.")

    def handle_answer(answer):
        try:
            answer = int(answer)
        except ValueError:
            return False
        if check(answer):
            print("✅ Correct!")
            return True
        else:
            print("❌ Incorrect.")
            return False

    check = generate_function() # This will return a boolean

    while True:
        command = input("\n> ").strip().lower()

        if command == "?":
            handle_help()

        elif command.startswith("answer "):
            answer = command[7:].strip()
            result = handle_answer(answer)
            return result

        elif command == "pause":
            print("⏸️ Game paused. Your progress has been saved.")
            try:
                save_state(state)
            finally:
                sys.exit()

        elif command == "quit":
            print("👋 You drop your backpack, leave the maze behind, and step back into the real world. Progress not saved.")
            try:
                clear_state()
                reset_state(state)
            finally:
                sys.exit()

        else:
            print("❓ Unknown command. Type '?' to see available commands.")


