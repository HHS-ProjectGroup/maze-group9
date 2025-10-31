# -----------------------------------------------------------------------------
# File: frontdeskoffice.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------

import random
import sys
import re
from persistence import save_state, clear_state, reset_state
from rooms.texts import FRONT_DESK_FAILED_CAPCHA, FRONT_DESK_LOOK_AROUND, FRONT_DESK_SOLVED_CAPCHA, type_rich
from .constants import ITEM_2, ROOM2
from .utils import display_status, handle_help_generic

# Holds the current puzzle hint text to print under the usage line
_CURRENT_MOVE_HINT = None


def _ensure_front_desk_state(state):
    # Initialize persistent state for this room
    if ROOM2 not in state["visited"]:
        state["visited"][ROOM2] = False
    # Legacy key cleanup/compat: ensure new puzzle state exists
    if "frontdesk_puzzle" not in state:
        state["frontdesk_puzzle"] = None  # will store dict with board, solution, id
    # Track last shown puzzle id to avoid immediate repeats
    if "frontdesk_last_puzzle_id" not in state:
        state["frontdesk_last_puzzle_id"] = None
    # Legacy compatibility for old tests referencing quiz
    if "frontdesk_question" not in state:
        state["frontdesk_question"] = None
    if "frontdesk_reward_spawned" not in state:
        state["frontdesk_reward_spawned"] = False


def _question_pool():
    """Legacy shim for tests that monkeypatch this symbol.
    Not used by the room logic anymore.
    """
    return [
        {
            "q": "Placeholder",
            "options": {"a": "A", "b": "B", "c": "C", "d": "D"},
            "correct": "a",
        }
    ]


def _puzzle_pool():
    # Three simple and logically valid "Checkmate in 1" puzzles.
    # Answers use the format: answer White queen to G8 (from-square optional)
    return [
        {
            "id": "p1",
            "title": "Checkmate in 1",
            "solution": {"color": "white", "piece": "queen", "from": "C1", "to": "C8"},
            "explanation": "Back-rank mate: the white queen on C1 checks along the back rank; the king cannot escape because e7 is blocked by its own pawn and there are no interpositions.",
            "pieces": {
                # Black
                "E8": "♚",
                "E7": "♟",
                "D7": "",
                "F7": "♟",
                # White
                "C1": "♕",
                "H1": "♔",
            },
        },
        {
            "id": "p2",
            "title": "Checkmate in 1",
            "solution": {"color": "white", "piece": "queen", "from": "G2", "to": "G8"},
            "explanation": "The queen ascends to G8 and mates along the back rank; the e7 pawn prevents the king from escaping to e7.",
            "pieces": {
                # Black
                "E8": "♚",
                "E7": "♟",
                "D7": "♝",
                # White
                "G2": "♕",
                "H1": "♔",
            },
        },
        {
            "id": "p3",
            "title": "Checkmate in 1",
            "solution": {"color": "white", "piece": "rook", "from": "H2", "to": "H8"},
            "explanation": "Rook to H8 delivers back-rank mate; the king cannot run to f7 or d7 because of White knight on E5 and there are no blocking moves.",
            "pieces": {
                # Black
                "E8": "♚",
                "E7": "♟",
                # White
                "E5": "♘",
                "H2": "♖",
                "E1": "♔",
            },
        },
    ]


def _legend():
    # Print the same neat legend used on the right side of the board
    for line in _legend_lines():
        type_rich(line)
    # Contextual hint for the current challenge (printed under the usage line)
    if _CURRENT_MOVE_HINT:
        type_rich(_CURRENT_MOVE_HINT)


def _print_room_header(state):
    if state["visited"][ROOM2]:
        type_rich("""The desk looks the same as before, but the holographic glow has dimmed.
The air smells faintly of burnt circuitry.
The coffee is cold now.
The terminal still sits there, logged out and unresponsive — like the room itself is done talking.
The battery slot under the desk is empty.""")

    else:
     type_rich("""You step into the Front Desk Office.
The air feels warmer here, as if the ventilation is still running.
A single desk stands in the center, covered with faint holographic residue.
A terminal hums quietly — still logged in, its display frozen on a half-written email.
Papers and notes are scattered around; a coffee cup rests by the keyboard, still half full.
Whoever worked here must’ve left in a hurry.""")

def _look_around():
    FRONT_DESK_LOOK_AROUND()

def _pick_new_puzzle(state):
    global _CURRENT_MOVE_HINT
    pool = _puzzle_pool()
    last_id = state.get("frontdesk_last_puzzle_id")
    candidates = [p for p in pool if p.get("id") != last_id] if (last_id and len(pool) > 1) else pool
    chosen = random.choice(candidates)
    state["frontdesk_puzzle"] = chosen
    state["frontdesk_last_puzzle_id"] = chosen.get("id")
    # Set contextual hint under the usage line based on the chosen puzzle
    pid = chosen.get("id")
    if pid == "p1":
        _CURRENT_MOVE_HINT = "Hint: Move White Queen on C1"
    elif pid == "p2":
        _CURRENT_MOVE_HINT = "Hint: Move White Queen on G2"
    elif pid == "p3":
        _CURRENT_MOVE_HINT = "Hint: Move White Rook on H2"
    else:
        _CURRENT_MOVE_HINT = None


def _render_chessboard(pieces: dict):
    # Render a chessboard using ASCII with Unicode chess symbols.
    files_lower = ["a", "b", "c", "d", "e", "f", "g", "h"]
    ranks = ["8", "7", "6", "5", "4", "3", "2", "1"]
    header = "    " + "   ".join(files_lower)
    separator = "  +---+---+---+---+---+---+---+---+"
    type_rich(header)
    type_rich(separator)
    for r in ranks:
        cells = []
        for f in files_lower:
            key = f.upper() + r
            symbol = pieces.get(key, " ") or " "
            cells.append(symbol)
        type_rich(f"{r} | " + " | ".join(cells) + f" | {r}")
        type_rich(separator)
    type_rich(header)


def _show_puzzle(state):
    p = state["frontdesk_puzzle"]
    if not p:
        _pick_new_puzzle(state)
        p = state["frontdesk_puzzle"]
    type_rich(f"\n{p['title']}: White to move and checkmate in 1")
    pieces = p.get("pieces")
    if isinstance(pieces, dict):
        _print_board_with_legend(pieces)
    else:
        # Fallback to pre-rendered board string
        type_rich(p.get("board", ""))
        _legend()


def _print_commands(state):
    # Keep the contextual usage line and dynamic hint on first visit
    if not state["visited"][ROOM2]:
        type_rich("\nType your move like: answer White queen to G8")
        if _CURRENT_MOVE_HINT:
            type_rich(_CURRENT_MOVE_HINT)

    # Build room-specific commands and delegate printing to the generic helper
    specifics: dict[str, str] = {}

    if not state["visited"][ROOM2]:
        specifics["answer <Color> <Piece> to <To>"] = "e.g., answer White queen to G8"

    if state["visited"][ROOM2] and state["frontdesk_reward_spawned"] and ITEM_2 not in state["inventory"]:
        specifics[f"take {ITEM_2}"] = f"Pick up the {ITEM_2} reward."

    handle_help_generic(ROOM2, specifics)


def _parse_answer(text: str):
    # Accept variants like the NEW preferred format:
    #   "answer White queen to G8"
    # and legacy variants:
    #   "answer White queen G2 to G8" or "answer White queen on G2 to G8"
    t = text.strip()
    # First try: with an explicit from-square (supports optional 'on' and arrow separators)
    m_full = re.match(r"^answer\s+([a-zA-Z]+)\s+([a-zA-Z]+)\s+(?:on\s+)?([a-hA-H][1-8])\s*(?:to|->|\-)\s*([a-hA-H][1-8])$", t)
    if m_full:
        color, piece, sq_from, sq_to = m_full.groups()
        return {
            "color": color.lower(),
            "piece": piece.lower(),
            "from": sq_from.upper(),
            "to": sq_to.upper(),
        }
    # Second try: short form without from-square
    m_short = re.match(r"^answer\s+([a-zA-Z]+)\s+([a-zA-Z]+)\s*(?:to|->|\-)\s*([a-hA-H][1-8])$", t)
    if m_short:
        color, piece, sq_to = m_short.groups()
        return {
            "color": color.lower(),
            "piece": piece.lower(),
            "from": None,
            "to": sq_to.upper(),
        }
    return None


def enter_frontdeskoffice(state):
    _ensure_front_desk_state(state)

    # Always show header on entering
    _print_room_header(state)

    # If solved previously, show post-completion greeting; do not auto-print commands
    if state["visited"][ROOM2]:
        pass
    else:
        # First-time entry: select or show a puzzle
        # Always pick a fresh random puzzle whenever the player enters this room (until solved)
        _pick_new_puzzle(state)
        _show_puzzle(state)

    # Main command loop for the room
    while True:
        raw = input("\n> ").strip()
        command = raw.lower()

        if command == "?":
            _print_commands(state)
            continue

        if command == "look around":
            _look_around()
            if not state["visited"][ROOM2]:
                state["score"] += 20
                _show_puzzle(state)
            continue

        if command in ["go back", "go corridor", "back"]:
            type_rich("You step away from the holographic desk and return to the corridor.")
            state["previous_room"] = ROOM2
            return "corridor"

        if command.startswith("answer "):
            if state["visited"][ROOM2]:
                type_rich("No more questions to answer.")
                continue
            parsed = _parse_answer(raw)
            if not parsed:
                type_rich("example answer: answer White queen to B8")
                _legend()
                continue
            p = state["frontdesk_puzzle"]
            if not p:
                _pick_new_puzzle(state)
                p = state["frontdesk_puzzle"]
            sol = p["solution"]
            # Accept correct move by destination only when from-square is omitted; remain strict if provided.
            if parsed["from"] is None:
                move_match = (parsed["to"] == sol["to"])  # short form
            else:
                move_match = (parsed["from"] == sol["from"]) and (parsed["to"] == sol["to"])  # legacy form
            strict_match = (
                parsed["color"] == sol["color"]
                and parsed["piece"] == sol["piece"]
                and (parsed["to"] == sol["to"])  # ensure same destination
            )
            if move_match or strict_match:
                type_rich("\n[Cyber Receptionist]: ‘Correct. Accept your reward…’")
                type_rich(f"The Cyber Receptionist places a {ITEM_2} on the desk in front of you.")
                type_rich(f"The {ITEM_2} hums softly with stored energy.")
                # Spawn {ITEM_2} in the room (once)
                state["frontdesk_reward_spawned"] = True
                state["visited"][ROOM2] = True
                state["score"] += 50
                # After success, no new questions; player can type '?' to see available commands
            else:
                FRONT_DESK_FAILED_CAPCHA()
                state["score"] -= 50
                state["frontdesk_question"] = None  # ensure a fresh random on next entry
                type_rich("[Cyber Receptionist]: ‘Incorrect. EJECTING…’", dialog=True)
                type_rich("You are flung out into the corridor!")
                state["frontdesk_puzzle"] = None  # ensure a fresh random on next entry
                state["previous_room"] = ROOM2
                return "corridor"
            continue

        if command.startswith("take "):
            item = raw[5:].strip().lower()
            if item == ITEM_2:
                if state["visited"][ROOM2] and state["frontdesk_reward_spawned"]:
                    if ITEM_2 in state["inventory"]:
                        type_rich(f"You already took the {ITEM_2}.")
                    else:
                        state["score"] += 200
                        type_rich(f"🔋 You take the {ITEM_2} and store it in your backpack.")
                        state["inventory"].append(ITEM_2)
                        # {ITEM_2} picked up; keep reward flag so no new {ITEM_2} spawns
                    # Type '?' to see available commands
                else:
                    type_rich(f"There is no {ITEM_2} available right now.")
            else:
                type_rich(f"There is no '{item}' to take here.")
            continue

        if command == "display status":
            display_status(state)
            continue

        if command == "pause":
            type_rich("⏸️ Game paused. Your progress has been saved.")
            try:
                save_state(state)
            finally:
                sys.exit()

        if command == "quit":
            type_rich("👋 You leave the front desk behind. Progress not saved.")
            try:
                clear_state()
                reset_state(state)
            finally:
                sys.exit()

        type_rich("❓ Unknown command. Type '?' to see available commands.")


# --- Helpers to render board and legend side by side ---

def _build_board_lines(pieces: dict):
    files_lower = ["a", "b", "c", "d", "e", "f", "g", "h"]
    ranks = ["8", "7", "6", "5", "4", "3", "2", "1"]
    header = "    " + "   ".join(files_lower)
    separator = "  +" + "---+" * 8
    lines = [header, separator]

    for r in ranks:
        row = []
        for f in files_lower:
            key = f.upper() + r
            symbol = pieces.get(key, " ") or " "
            # Center each piece or space within 3-character cell
            cell = f" {symbol} "
            row.append(cell)
        lines.append(f"{r} |" + "|".join(row) + f"| {r}")
        lines.append(separator)
    lines.append(header)
    return lines


def _legend_lines():
    """Build a neat, boxed legend to be shown on the right of the board.
    Two aligned columns: White pieces | Black pieces.
    """
    title = "Piece Legend"

    left_title = "White pieces"
    right_title = "Black pieces"

    left_items = [
        ("King", "♔"),
        ("Queen", "♕"),
        ("Rook", "♖"),
        ("Bishop", "♗"),
        ("Knight", "♘"),
        ("Pawn", "♙"),
    ]
    right_items = [
        ("King", "♚"),
        ("Queen", "♛"),
        ("Rook", "♜"),
        ("Bishop", "♝"),
        ("Knight", "♞"),
        ("Pawn", "♟"),
    ]

    left_lines = [f"{name}: {sym}" for name, sym in left_items]
    right_lines = [f"{name}: {sym}" for name, sym in right_items]

    left_width = max(len(left_title), max((len(s) for s in left_lines), default=0))
    right_width = max(len(right_title), max((len(s) for s in right_lines), default=0))
    gap = "   "  # spacing between columns

    total_inner = left_width + len(gap) + right_width

    top = "+" + "-" * (total_inner + 2) + "+"
    title_line = "| " + title.center(total_inner) + " |"
    header_line = (
        "| "
        + left_title.ljust(left_width)
        + gap
        + right_title.ljust(right_width)
        + " |"
    )
    sep_line = "| " + ("-" * left_width) + gap + ("-" * right_width) + " |"

    # Compose rows
    row_count = max(len(left_lines), len(right_lines))
    rows = []
    for i in range(row_count):
        left = left_lines[i] if i < len(left_lines) else ""
        right = right_lines[i] if i < len(right_lines) else ""
        rows.append(
            "| " + left.ljust(left_width) + gap + right.ljust(right_width) + " |"
        )

    bottom = "+" + "-" * (total_inner + 2) + "+"

    return [
        top,
        title_line,
        header_line,
        sep_line,
        *rows,
        sep_line,
        bottom,
        "",
    ]


def _print_board_with_legend(pieces: dict):
    board_lines = _build_board_lines(pieces)
    legend_lines = _legend_lines()
    left_width = max(len(line) for line in board_lines)
    gap = "   "
    total_lines = max(len(board_lines), len(legend_lines))

    for i in range(total_lines):
        left = board_lines[i] if i < len(board_lines) else " " * left_width
        right = legend_lines[i] if i < len(legend_lines) else ""
        type_rich(left.ljust(left_width) + gap + right)
