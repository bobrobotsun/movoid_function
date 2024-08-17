import builtins
import sys


def do_error(text):
    print(text, file=sys.stderr)


class Test_builtins:
    def test_01_replace_print(self):
        setattr(builtins, 'error', do_error)
        error(123)
