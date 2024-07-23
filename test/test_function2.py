import sys

from movoid_function import replace_function, ReplaceFunction, restore_function


class Test_class_ReplaceFunction2:
    def test_01_replace_print_cross_file(self):
        def other_print(*args, sep=' ', end='\n'):
            arg_list = [str(_) for _ in args]
            print_text = 'this is test print:' + str(sep).join(arg_list) + str(end)
            sys.stdout.write(print_text)
            return print_text

        replace_function(print, other_print)
