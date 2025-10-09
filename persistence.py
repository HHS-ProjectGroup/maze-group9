# -----------------------------------------------------------------------------
# File: persistence.py
# Purpose: Save/load game state to a local SQLite database.
# -----------------------------------------------------------------------------
from __future__ import annotations

import json
import os
import sqlite3
from typing import Optional, Dict, Any

DEFAULT_DB = os.path.join(os.path.dirname(__file__), "game_state.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS game_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    state_json TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

UPSERT = """
INSERT INTO game_state (id, state_json) VALUES (1, ?)
ON CONFLICT(id) DO UPDATE SET state_json=excluded.state_json, updated_at=CURRENT_TIMESTAMP;
"""

SELECT_ONE = "SELECT state_json FROM game_state WHERE id = 1 LIMIT 1;"


def _connect(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = db_path or DEFAULT_DB
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    return conn


def save_state(state: Dict[str, Any], db_path: Optional[str] = None) -> None:
    """Persist the full state dict into SQLite as a JSON string.

    Args:
        state: The full game state dictionary.
        db_path: Optional path to the SQLite DB file.
    """
    # Ensure the state is JSON serializable (lists, dicts, bools, ints, strings OK)
    payload = json.dumps(state)
    with _connect(db_path) as conn:
        conn.execute(SCHEMA)
        conn.execute(UPSERT, (payload,))
        conn.commit()


def load_state(db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Load previously saved game state from SQLite.

    Returns the state dict if found, otherwise None.
    """
    try:
        with _connect(db_path) as conn:
            conn.execute(SCHEMA)
            cur = conn.execute(SELECT_ONE)
            row = cur.fetchone()
            if not row:
                return None
            return json.loads(row[0])
    except Exception:
        # If anything goes wrong (e.g., corrupted DB), start fresh
        return None


# Additional helpers for resetting and clearing state
DELETE_ONE = "DELETE FROM game_state WHERE id = 1;"


def clear_state(db_path: Optional[str] = None) -> None:
    """Remove any saved game state from the database.

    After calling this, a subsequent load_state() will return None and the game
    should start with default values.
    """
    with _connect(db_path) as conn:
        conn.execute(SCHEMA)
        conn.execute(DELETE_ONE)
        conn.commit()


def get_default_state() -> Dict[str, Any]:
    """Return a fresh default game state dictionary."""
    return {
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
        # New fields to persist across sessions
        "score": 0,
        "elapsed_seconds": 0.0,
        "game_beaten": False,
    }


def reset_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Reset the provided state dict in-place to default values and return it."""
    defaults = get_default_state()
    state.clear()
    state.update(defaults)
    return state
