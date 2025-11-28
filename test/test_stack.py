import sys

from movoid_function import STACK, wraps


class Test_class_Stack:
    def test_01_STACK_initial_ignore_list(self):
        assert len(STACK.ignore_list) == 6
        assert STACK.ignore_list[0] == (r'E:\000develop\movoid_function\movoid_function\decorator.py', 377, None)
        assert STACK.ignore_list[1] == (r"E:\000develop\movoid_function\movoid_function\decorator.py", 668, None)
        assert STACK.ignore_list[2] == (r"E:\000develop\movoid_function\movoid_function\decorator.py", 716, None)
        assert STACK.ignore_list[3] == (r"E:\000develop\movoid_function\movoid_function\decorator.py", 763, None)
        assert STACK.ignore_list[4] == (r"E:\000develop\movoid_function\movoid_function\decorator.py", 432, None)
        assert STACK.ignore_list[5] == (r"E:\000develop\movoid_function\movoid_function\decorator.py", 488, None)

    def test_02_get_stack_info(self):
        assert STACK.get_simple_frame_info(0) == (__file__, 17, 'test_02_get_stack_info')

    def test_03___call__(self):
        stack = STACK(sys._getframe())
        assert stack.info == (__file__, 20, 'test_03___call__')

    def test_04_dec_info(self):
        print_list = []

        def print_log(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                print_list.append(STACK(func).info)
                print_list.append(STACK.get_simple_frame_info(1))
                re_value = func(*args, **kwargs)
                return re_value

            return wrapper

        @print_log
        def temp1():
            print_list.append('temp1 start')
            print_list.append(STACK.get_simple_frame_info(0))
            print_list.append(STACK.get_simple_frame_info(1))
            print_list.append('temp1 end')

        @print_log
        def temp2():
            print_list.append('temp2 start')
            temp1()
            print_list.append('temp2 end')

        STACK.file_should_ignore(__file__, 're_value = func(*args, **kwargs)')
        temp2()
        assert print_list[0] == ('E:\\000develop\\movoid_function\\test\\test_stack.py', 43, 'temp2')
        assert print_list[1] == ('E:\\000develop\\movoid_function\\test\\test_stack.py', 50, 'test_04_dec_info')
        assert print_list[2] == 'temp2 start'
        assert print_list[3] == ('E:\\000develop\\movoid_function\\test\\test_stack.py', 36, 'temp1')
        assert print_list[4] == ('E:\\000develop\\movoid_function\\test\\test_stack.py', 46, 'temp2')
        assert print_list[5] == 'temp1 start'
        assert print_list[6] == ('E:\\000develop\\movoid_function\\test\\test_stack.py', 39, 'temp1')
        assert print_list[7] == ('E:\\000develop\\movoid_function\\test\\test_stack.py', 46, 'temp2')
        assert print_list[8] == 'temp1 end'
        assert print_list[9] == 'temp2 end'
