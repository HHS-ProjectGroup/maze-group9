import csv
import os
import time
from typing import List, Tuple

LEADERBOARD_FILE = "leaderboard.csv"
MAX_ENTRIES = 10


def _file_path() -> str:
    return os.path.join(os.path.dirname(__file__), LEADERBOARD_FILE)


def load_leaderboard() -> List[Tuple[str, int, float]]:
    path = _file_path()
    if not os.path.exists(path):
        return []
    entries: List[Tuple[str, int, float]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                name, score, seconds = row[0], int(row[1]), float(row[2])
                entries.append((name, score, seconds))
            except Exception:
                # skip malformed rows
                continue
    return entries


def sort_entries(entries: List[Tuple[str, int, float]]) -> List[Tuple[str, int, float]]:
    # Highest score first, then fastest time (lowest seconds)
    return sorted(entries, key=lambda x: (-x[1], x[2]))[:MAX_ENTRIES]


def save_leaderboard(entries: List[Tuple[str, int, float]]) -> None:
    entries = sort_entries(entries)
    path = _file_path()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for name, score, seconds in entries:
            writer.writerow([name, score, f"{seconds:.3f}"])


def append_result(name: str, score: int, seconds: float) -> None:
    entries = load_leaderboard()
    entries.append((name, score, seconds))
    save_leaderboard(entries)


def print_leaderboard(entries: List[Tuple[str, int, float]] | None = None) -> None:
    if entries is None:
        entries = load_leaderboard()
    entries = sort_entries(entries)
    print("==== Leaderboard (Top 10) ====")
    if not entries:
        print("No results yet. Be the first to set a score!")
        return
    print("#  Name                 Score   Time (s)")
    for i, (name, score, seconds) in enumerate(entries, start=1):
        print(f"{i:>2}. {name[:18]:<18}  {score:>5}   {seconds:>7.2f}")


class GameTimer:
    def __init__(self):
        self.start_time: float | None = None
        self.end_time: float | None = None

    def start(self):
        self.start_time = time.perf_counter()

    def stop(self) -> float:
        self.end_time = time.perf_counter()
        return self.elapsed()

    def elapsed(self) -> float:
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time is not None else time.perf_counter()
        return max(0.0, end - self.start_time)