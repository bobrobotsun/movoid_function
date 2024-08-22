#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : test_decorator
# Author        : Sun YiFan-Movoid
# Time          : 2024/8/22 22:40
# Description   : 
"""
from movoid_function import wraps, decorate_class_function_include, decorate_class_function_exclude


def dec(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return len(args)

    return wrapper


def dec2(re_value):
    def dec_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return re_value

        return wrapper

    return dec_wrapper


class Test_function_decorate_class_function_include:
    def test_basic(self):
        @decorate_class_function_include(dec, '^do')
        class Test1:
            def do_it(self):
                return 'a'

            def it_do(self):
                return 'b'

            def __str__(self):
                return 'Test1'

        test1 = Test1()
        assert test1.do_it() == 1
        assert test1.it_do() == 'b'
        assert str(test1) == 'Test1'

    def test_param_true(self):
        @decorate_class_function_include(dec2, '^do', param=True, args=[2])
        class Test1:
            def do_it(self):
                return 'a'

            def it_do(self):
                return 'b'

            def __str__(self):
                return 'Test1'

        test1 = Test1()
        assert test1.do_it() == 2
        assert test1.it_do() == 'b'
        assert str(test1) == 'Test1'


class Test_function_decorate_class_function_exclude:
    def test_basic(self):
        @decorate_class_function_exclude(dec, '^do')
        class Test1:
            def do_it(self):
                return 'a'

            def it_do(self):
                return 'b'

            def __str__(self):
                return 'Test1'

        test1 = Test1()
        assert test1.do_it() == 'a'
        assert test1.it_do() == 1
        assert str(test1) == 'Test1'

    def test_param_true(self):
        @decorate_class_function_exclude(dec2, '^do', param=True, args=[2])
        class Test1:
            def do_it(self):
                return 'a'

            def it_do(self):
                return 'b'

            def __str__(self):
                return 'Test1'

        test1 = Test1()
        assert test1.do_it() == 'a'
        assert test1.it_do() == 2
        assert str(test1) == 'Test1'
