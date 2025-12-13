import pathlib
import sys

from movoid_function import STACK, wraps, stack


class Test_class_Stack:
    def test_01_STACK_initial_ignore_list(self):
        assert len(STACK.ignore_list) == 6
        STACK.self_check()

    def test_02_get_stack_info(self):
        stack_frame = STACK.get_frame()
        assert stack_frame.info(stack.PathFunction) == f'{pathlib.Path(__file__)}:13:test_02_get_stack_info'

    def test_03___call__(self):
        stack_frame = STACK(sys._getframe())
        assert stack_frame.info(stack.PathFunction) == f'{pathlib.Path(__file__)}:17:test_03___call__'

    def test_04_dec_info(self):
        print_list = []

        def print_log(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                print_list.append(STACK.get_frame(1).info(stack.PathFunction))
                re_value = func(*args, **kwargs)
                return re_value

            return wrapper

        @print_log
        def temp1():
            print_list.append('temp1 start')
            print_list.append(STACK.get_frame().info(stack.PathFunction))
            print_list.append(STACK.get_frame(1).info(stack.PathFunction))
            print_list.append('temp1 end')

        @print_log
        def temp2():
            print_list.append('temp2 start')
            temp1()
            print_list.append('temp2 end')

        STACK.this_file_lineno_should_ignore(27, check_text='re_value = func(*args, **kwargs)')
        temp2()
        assert print_list[0] == f'{pathlib.Path(__file__)}:46:test_04_dec_info'
        assert print_list[1] == 'temp2 start'
        assert print_list[2] == f'{pathlib.Path(__file__)}:42:temp2'
        assert print_list[3] == 'temp1 start'
        assert print_list[4] == f'{pathlib.Path(__file__)}:35:temp1'
        assert print_list[5] == f'{pathlib.Path(__file__)}:42:temp2'
        assert print_list[6] == 'temp1 end'
        assert print_list[7] == 'temp2 end'
        STACK.self_check()
