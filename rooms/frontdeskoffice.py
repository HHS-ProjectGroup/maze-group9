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
from rooms.texts import FRNT_DSK_FAILED_CAPCHA, FRNT_DSK_LOOK_AROUND, FRNT_DSK_SOLVED_CAPCHA, type_rich
from .constants import ITEM_2, ROOM2
from .utils import display_status, handle_help_generic


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
    # Answers use the format: answer White rook A1 to A7
    return [
        {
            "id": "p1",
            "title": "Checkmate in 1",
            # White to move: Rook from A1 to A8 delivers mate. Black king has no escape (e7 is blocked).
            "solution": {"color": "white", "piece": "rook", "from": "A1", "to": "A8"},
            "explanation": "Back-rank mate: the rook on A8 checks along the 8th rank; the king cannot escape because e7 is blocked by its own pawn and there are no interpositions.",
            "pieces": {
                # Black
                "E8": "♚",
                "E7": "♟",
                # White
                "A1": "♖",
                "H1": "♔",
            },
        },
        {
            "id": "p2",
            "title": "Checkmate in 1",
            # White to move: Queen from G2 to G8 mates (same back-rank idea; e7 blocked).
            "solution": {"color": "white", "piece": "queen", "from": "G2", "to": "G8"},
            "explanation": "The queen ascends to G8 and mates along the back rank; the e7 pawn prevents the king from escaping to e7.",
            "pieces": {
                # Black
                "E8": "♚",
                "E7": "♟",
                # White
                "G2": "♕",
                "H1": "♔",
            },
        },
        {
            "id": "p3",
            "title": "Checkmate in 1",
            # White to move: Rook from H1 to H8 mates (back-rank mate with e7 blocked).
            "solution": {"color": "white", "piece": "rook", "from": "H1", "to": "H8"},
            "explanation": "Rook to H8 delivers back-rank mate; the king cannot run to e7 and there are no blocking moves.",
            "pieces": {
                # Black
                "E8": "♚",
                "E7": "♟",
                # White
                "H1": "♖",
                "A1": "♔",
            },
        },
    ]


def _legend():
    print("\nPiece Legend:")
    print("♔ = White King      ♚ = Black King")
    print("♕ = White Queen     ♛ = Black Queen")
    print("♖ = White Rook      ♜ = Black Rook")
    print("♗ = White Bishop    ♝ = Black Bishop")
    print("♘ = White Knight    ♞ = Black Knight")
    print("♙ = White Pawn      ♟ = Black Pawn")
    print(".  = Empty square")
    print("\nType your move like: answer White rook A1 to A7")


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
    FRNT_DSK_LOOK_AROUND()

def _pick_new_puzzle(state):
    pool = _puzzle_pool()
    last_id = state.get("frontdesk_last_puzzle_id")
    candidates = [p for p in pool if p.get("id") != last_id] if (last_id and len(pool) > 1) else pool
    chosen = random.choice(candidates)
    state["frontdesk_puzzle"] = chosen
    state["frontdesk_last_puzzle_id"] = chosen.get("id")


def _render_chessboard(pieces: dict):
    # Render a chessboard using ASCII exactly like the requested style.
    files_lower = ["a", "b", "c", "d", "e", "f", "g", "h"]
    ranks = ["8", "7", "6", "5", "4", "3", "2", "1"]
    header = "    " + "   ".join(files_lower)
    separator = "  +---+---+---+---+---+---+---+---+"
    print(header)
    print(separator)
    for r in ranks:
        cells = []
        for f in files_lower:
            key = f.upper() + r
            symbol = pieces.get(key, " ")
            if not symbol:
                symbol = " "
            cells.append(symbol)
        print(f"{r} | " + " | ".join(cells) + f" | {r}")
        print(separator)
    print(header)


def _show_puzzle(state):
    p = state["frontdesk_puzzle"]
    if not p:
        _pick_new_puzzle(state)
        p = state["frontdesk_puzzle"]
    print(f"\n{p['title']}: White to move and checkmate in 1")
    pieces = p.get("pieces")
    if isinstance(pieces, dict):
        _print_board_with_legend(pieces)
    else:
        # Fallback to pre-rendered board string
        print(p.get("board", ""))
        _legend()


def _print_commands(state):
    if not state["visited"][ROOM2]:
        print("\nType your move like: answer White rook A1 to A7")
    print("\nAvailable commands:")
    entries = []
    if not state["visited"][ROOM2]:
        entries.append(("- answer <Color> <Piece> <From> to <To>", ": Answer White rook A1 to A7"))
    if state["visited"][ROOM2] and state["frontdesk_reward_spawned"] and ITEM_2 not in state["inventory"]:
        entries.append((f"- take {ITEM_2}", f": Pick up the {ITEM_2} reward."))
    entries.extend([
        ("- leave", ": Exit to the corridor."),
        ("- ?", ": Show this help message."),
        ("- look around", ": Reprint description and your options."),
        ("- display status", ": Show your inventory, location, and visited rooms."),
        ("- pause", ": Save and exit (pause the game)."),
        ("- quit", ": Quit without saving."),
    ])
    left_width = max(len(left) for left, _ in entries) if entries else 0
    for left, right in entries:
        print(left.ljust(left_width) + "  " + right)


def _parse_answer(text: str):
    # Accept variants like: "answer White rook A1 to A7" or arrows
    # Normalize spacing and separators
    m = re.match(r"^answer\s+([a-zA-Z]+)\s+([a-zA-Z]+)\s+([a-hA-H][1-8])\s*(?:to|->|\-)\s*([a-hA-H][1-8])$", text.strip())
    if not m:
        return None
    color, piece, sq_from, sq_to = m.groups()
    return {
        "color": color.lower(),
        "piece": piece.lower(),
        "from": sq_from.upper(),
        "to": sq_to.upper(),
    }


def enter_frontdeskoffice(state):
    _ensure_front_desk_state(state)

    # Always show header on entering
    _print_room_header(state)

    # If solved previously, show post-completion greeting and commands, no puzzles
    if state["visited"][ROOM2]:
        _print_commands(state)
    else:
        # First-time entry: select or show a puzzle
        # Always pick a fresh random puzzle whenever the player enters this room (until solved)
        _pick_new_puzzle(state)
        _show_puzzle(state)
        _print_commands(state)

    # Main command loop for the room
    while True:
        raw = input("\n> ").strip()
        command = raw.lower()

        if command in ("?", "help"):
            _print_commands(state)
            continue

        if command == "look around":
            _look_around()
            if not state["visited"][ROOM2]:
                _show_puzzle(state)
            _print_commands(state)
            continue

        if command == "leave" or command == "go corridor" or command == "back":
            type_rich("You step away from the holographic desk and return to the corridor.")
            state["previous_room"] = ROOM2
            return "corridor"

        if command.startswith("answer "):
            if state["visited"][ROOM2]:
                type_rich("No more questions to answer.")
                continue
            parsed = _parse_answer(raw)
            if not parsed:
                type_rich("Please answer like: answer White rook A1 to A7")
                _legend()
                continue
            p = state["frontdesk_puzzle"]
            if not p:
                _pick_new_puzzle(state)
                p = state["frontdesk_puzzle"]
            sol = p["solution"]
            # Accept correct move even if the player mistypes color/piece words.
            same_move = (parsed["from"] == sol["from"]) and (parsed["to"] == sol["to"])
            strict_match = (
                parsed["color"] == sol["color"]
                and parsed["piece"] == sol["piece"]
                and same_move
            )
            if same_move or strict_match:
                print("\n[Cyber Receptionist]: ‘Correct. Accept your reward…’")
                print(f"The Cyber Receptionist places a {ITEM_2} on the desk in front of you.")
                print(f"The {ITEM_2} hums softly with stored energy.")
                # Spawn {ITEM_2} in the room (once)
                state["frontdesk_reward_spawned"] = True
                state["visited"][ROOM2] = True
                # After success, no new questions; show that {ITEM_2} can be taken
                _print_commands(state)
            else:
                FRNT_DSK_FAILED_CAPCHA()
                state["frontdesk_question"] = None  # ensure a fresh random on next entry
                print("\n[Cyber Receptionist]: ‘Incorrect. EJECTING…’")
                print("You are flung out into the corridor!")
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
                        type_rich(f"🔋 You take the {ITEM_2} and store it in your backpack.")
                        state["inventory"].append(ITEM_2)
                        # {ITEM_2} picked up; keep reward flag so no new {ITEM_2} spawns
                    _print_commands(state)
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
    separator = "  +---+---+---+---+---+---+---+---+"
    lines = [header, separator]
    for r in ranks:
        cells = []
        for f in files_lower:
            key = f.upper() + r
            symbol = pieces.get(key, " ") or " "
            cells.append(symbol)
        lines.append(f"{r} | " + " | ".join(cells) + f" | {r}")
        lines.append(separator)
    lines.append(header)
    return lines


def _legend_lines():
    return [
        "Piece Legend:",
        "♔ = White King      ♚ = Black King",
        "♕ = White Queen     ♛ = Black Queen",
        "♖ = White Rook      ♜ = Black Rook",
        "♗ = White Bishop    ♝ = Black Bishop",
        "♘ = White Knight    ♞ = Black Knight",
        "♙ = White Pawn      ♟ = Black Pawn",
        "   = Empty square",
        "",
    ]


def _print_board_with_legend(pieces: dict):
    board_lines = _build_board_lines(pieces)
    legend_lines = _legend_lines()
    left_width = max((len(s) for s in board_lines), default=0)
    gap = "   "
    total = max(len(board_lines), len(legend_lines))
    for i in range(total):
        left = board_lines[i] if i < len(board_lines) else "".ljust(left_width)
        if len(left) < left_width:
            left = left + (" " * (left_width - len(left)))
        right = legend_lines[i] if i < len(legend_lines) else ""
        print(left + gap + right)
