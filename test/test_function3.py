import sys

from movoid_function import replace_function, ReplaceFunction, restore_function


class Test_class_ReplaceFunction3:
    def test_01_replace_print_cross_file(self):
        assert type(print) is ReplaceFunction
        assert print('a', 123, True, None, sep='-', end='~~') == 'this is test print:a-123-True-None~~'
