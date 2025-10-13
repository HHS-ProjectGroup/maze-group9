import builtins
from unittest.mock import patch


def run_game_with_commands(commands, entrypoint, state, capsys):
    """ """
    commands_iter = iter(commands)

    def fake_input(_=None):
        try:
            val = next(commands_iter)
            print(
                f"> {val}{5 * ' '}<{80 * '-'}>{5 * ' '}INPUT"
            )  # This is the simplest way to add our inputs to log, as we patched print
            return val
        except StopIteration:
            raise SystemExit("No more commands!")

    with patch.object(builtins, "input", fake_input):
        try:
            result = entrypoint(state)
        except SystemExit:
            result = None
    captured = capsys.readouterr()

    return result, captured, state
