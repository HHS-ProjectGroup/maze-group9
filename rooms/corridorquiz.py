import random

def generate_quadratic_inequality():

    # generate the inequality again if it has no solutions
    def has_solution(sign, delta):

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

    while True:
        a = random.randint(-10, 10)  # nonzero
        # regenerate if a is equal to 0
        if a == 0:
            continue
        b = random.randint(-20, 20)
        c = random.randint(-50, 50)
        # I'm going to need to exclude 0 values for b and c

        sign_function = ""

        # Random inequality sign will depend on the sign of c
        if c > 0:
            sign_function= "<"
        else:
            sign_function = ">"

        delta_function = b ** 2 - 4 * a * c

        if has_solution(sign_function, delta_function):
            break

    print(f"Solve: {a}x² + {b}x + {c} {sign_function} 0")

    return lambda x: eval(f"{a}*x**2 + {b}*x + {c} {sign_function} 0")

# Example use
def random_quiz_corridor():
    check = generate_quadratic_inequality()
    while True:
        try:
            user_input = int(input("Enter an integer that satisfies the inequality: "))
            break  # exit loop if conversion succeeds
        except ValueError:
            print("❌ Invalid input. Please enter an integer.")

    if check(user_input):
        print("✅ Correct!")
        return True
    else:
        print("❌ Incorrect.")
        return False