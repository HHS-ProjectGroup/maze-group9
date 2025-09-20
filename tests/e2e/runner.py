import builtins
from unittest.mock import patch


def run_game_with_commands(commands, entrypoint, state, capsys):
    """ """
    commands_iter = iter(commands)

    def fake_input(_=None):
        try:
            return next(commands_iter)
        except StopIteration:
            raise SystemExit("No more commands!")

    with patch.object(builtins, "input", fake_input):
        try:
            result = entrypoint(state)
        except SystemExit:
            result = None
    captured = capsys.readouterr()

    return result, captured, state
