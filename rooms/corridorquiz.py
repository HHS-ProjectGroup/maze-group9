import random
import sys


def generate_quadratic_inequality(state):

    def has_solution(sign, delta, a):

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

            if has_solution(sign_function, delta_function, a):
                break

        print(f"{a}x² + {b}x + {c} {sign_function} 0")

        return lambda x: eval(f"{a}*x**2 + {b}*x + {c} {sign_function} 0")

    def handle_help():
        print("\nAvailable commands:")
        if state["visited"]["classroom2015"] and "key" not in state["inventory"]:
            print("- take manual            : Pick up the manual once it's revealed.")
        print("- answer <number>     : Attempt to solve the math question.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game.")

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

        # --- Commandoloop ---

    check = generate_function()

    while True:
        command = input("\n> ").strip().lower()

        if command == "?":
            handle_help()

        elif command.startswith("answer "):
            answer = command[7:].strip()
            result = handle_answer(answer)
            return result

        elif command == "quit":
            print("👋 You drop your backpack, leave the maze behind, and step back into the real world.")
            sys.exit()

        else:
            print("❓ Unknown command. Type '?' to see available commands.")


