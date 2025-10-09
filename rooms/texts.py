from rich.text import Text
from rich.console import Console
import random
import time

from rooms.constants import ITEM_1

# In the better world there would be an IO class
# funcs
console = Console()

GLITCH_CHARS = list("!@#$%^&*()-_+=~?<>|\\/[]{}:;.,0123456789▒░█▓")
STOP_CHARS = " .,!?"
GLITCH_PROB_BASE = 0.04
GLITCH_PROB_STOP = 0.15

def _render_and_pad(text_obj: Text, prev_last_len: int) -> int:
    """
    Перерисовывает текущую (последнюю) строку: возвращает длину последней видимой строки.
    Работает путём \r + print(Text, end="") + удаление хвоста пробелами при необходимости.
    """
    console.file.write("\r")
    console.print(text_obj, end="", soft_wrap=False)
    plain_last = text_obj.plain.split("\n")[-1]
    cur_len = len(plain_last)

    extra = prev_last_len - cur_len
    if extra > 0:
        # затираем остатки предыдущей длинной строки пробелами
        console.file.write(" " * extra)
        console.file.write("\r")
        console.print(text_obj, end="", soft_wrap=False)

    console.file.flush()
    return cur_len

def _hide_cursor():
    """Попытаться скрыть курсор в терминале (ANSI)."""
    try:
        console.file.write("\x1b[?25l")
        console.file.flush()
    except Exception:
        pass

def _show_cursor():
    """Восстановить курсор."""
    try:
        console.file.write("\x1b[?25h")
        console.file.flush()
    except Exception:
        pass

def type_rich(raw_text: str, delay: float = 0.035, dialog: bool = False):
    """
    Печать с поддержкой Rich-разметки.
    - Для dialog=False: простой посимвольный вывод (без перерисовки) — максимально совместим.
    - Для dialog=True: включаем глитчи (временные последовательности), перерисовка строки для удаления мусора,
      и временно скрываем курсор для более чистого эффекта.
    """
    parsed = Text.from_markup(raw_text)

    if not dialog:
        try:
            _hide_cursor()
            for c in parsed:
                console.print(c, end="", soft_wrap=False)
                console.file.flush()
                ch = c.plain
                if ch == "\n":
                    time.sleep(delay * 1.2)
                elif ch in STOP_CHARS:
                    time.sleep(delay * 2.0 * random.uniform(0.7, 1.2))
                else:
                    time.sleep(delay * random.uniform(0.7, 1.3))
            console.print()
        finally:
            _show_cursor()
        return

    out = Text()
    prev_len = 0
    try:
        _hide_cursor()
        for c in parsed:
            ch = c.plain

            # возможность глитча
            glitch_prob = GLITCH_PROB_STOP if ch in STOP_CHARS else GLITCH_PROB_BASE
            if random.random() < glitch_prob:
                glitch_count = random.randint(2, 5)
                for _ in range(glitch_count):
                    gseq = "".join(random.choice(GLITCH_CHARS) for _ in range(random.randint(1, 3)))
                    temp = out + Text(gseq, style="bright_black")
                    prev_len = _render_and_pad(temp, prev_len)
                    time.sleep(random.uniform(0.02, 0.07))

            # добавляем реальный символ с сохранением стиля (если есть)
            style = getattr(c, "style", None)
            if style:
                out.append(ch, style=style)
            else:
                out.append(ch)

            prev_len = _render_and_pad(out, prev_len)

            # паузы
            if ch == "\n":
                prev_len = 0
                time.sleep(delay * 1.2)
            elif ch in STOP_CHARS:
                time.sleep(delay * 2.0 * random.uniform(0.7, 1.2))
            else:
                time.sleep(delay * random.uniform(0.7, 1.3))

        console.print()
    finally:
        _show_cursor()

# Start of the game

WELCOMING_TEXT_0 = lambda: type_rich(
    """[bold green]You open your eyes...[/bold green].
The floor feels cold, eventhough something evaporates.
A corridor stretches ahead, dim lights running along the floor in thin white lines. The air smells sterile, too clean. There’s no one here."""
)

WELCOMING_TEXT_1 = lambda: type_rich("""You try to remember your name, but nothing comes. Not even a face.
For some reason, one thought rises above the rest: chocolate milk.
""")

# Corridor

CORRIDOR_TEXT_UNVISITED_0 = lambda: type_rich("""You step into a long corridor. Thin white lines of light run along the floor — 
like guiding strips on an aircraft. The ceiling lamps are dark.  

A few thick stains stretch across the tiles — black and glossy, 
as if some machine had bled its oil here.  
Yet there’s no smell at all. No dust, no footprints. Everything is… *too clean.*  

The silence hums faintly, almost mechanical.  

At the far wall, a holo-poster flickers:
[bold cyan]"Dr. Mara Lin presents a new step in AGI: meet [bold deep_pink4]EDEN[/bold deep_pink4]! 11.11 — Main Hall, 1 PM"[/bold cyan]

You can almost feel it watching you through the static.  
Two doors on the left glow faintly through their glass — the rest are blurred, locked, or completely dark.  

Somewhere in the distance, a quiet electronic [bold]beep[/bold] echoes… then fades.
""")

CORRIDOR_TEXT_VISITED_0 = lambda: type_rich("""The corridor feels quieter now — as if the building knows you’ve been here before.  
The lights still pulse along the floor, tracing your path.  
The stains haven’t moved, but they seem darker.  

The holo-poster still loops its message about EDEN, but the color has shifted — 
more blue than before, colder.  

The air tastes metallic.
""")

CORRIDOR_TEXT_NO_ENCOUNTER = lambda: type_rich("You don't see any movement in the corridor. Yet you sure somebody is watching you")

CORRIDOR_TEXT_ENCOUNTE_0 = lambda: type_rich("""There’s a pulse — not of sound, but of light. The corridor freezes. On the far glass, a message fades in:""")

CORRIDOR_TEXT_ENCOUNTE_1 = lambda: type_rich("\"System requests participation in calibration.\"", dialog=True)

CORRIDOR_TEXT_ENCOUNTE_2 = lambda: type_rich("""The letters rearrange themselves into a mathematical question, as if drawn by invisible hands. You realize — it’s not a request.""")

CORRIDOR_TEXT_PROBLEM_SOLVED_0 = lambda: type_rich("\"Acceptable deviation. Cognitive pattern within expected range.\"", dialog=True)

CORRIDOR_TEXT_PROBLEM_FAILED_0 = lambda: type_rich("\"Cognitive inconsistency detected. Administering corrective feedback.\"", dialog=True)

CORRIDOR_TEXT_PROBLEM_FAILED_1 = lambda: type_rich("Suddenly you feel worse. It's definitely better to solve it next time. It's hard to evaluate, how much more you can take it")

def CORRIDOR_TEXT_REVIEL_ITEM():
    type_rich("After third problem is solved, you see one more message arising on the screen:")
    type_rich(f"\"This {ITEM_1} you might find usefull in the future. I recommend you take it.\"", dialog=True)

CORRIDOR_EMPTY = lambda: type_rich("Nothing had changed since you've been here. Maybe, some stains have gone smaller.")

# Front Desk

# Classroom 2015

# Project Room 3

# Study Landscape

# Lab03

# Lab01

# Generic


if __name__ == "__main__":
    CORRIDOR_TEXT_REVIEL_ITEM()
