#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : test_function
# Author        : Sun YiFan-Movoid
# Time          : 2024/7/21 1:00
# Description   : 
"""
import sys

import pytest
from movoid_function import Function, ReplaceFunction, replace_function, restore_function


class Test_class_Function:
    # def setup_class(self):
    #     print('setup class')

    def test_01_empty_function(self):
        empty = Function()
        assert empty(1) is None
        assert empty(a='1') is None
        assert empty(1, todo=None) is None

    def test_02_no_args_function(self):
        def model():
            return 1

        func = Function(model)

        assert func.id == id(model)
        assert func.name == 'model'
        assert func.file
        assert func.lineno
        assert func() == 1
        try:
            func(1)
        except TypeError:
            pass
        else:
            raise AssertionError('it should not allow to get arguments')
        try:
            func(a='1')
        except TypeError:
            pass
        else:
            raise AssertionError('it should not allow to get arguments')
        try:
            func(2, cc=True)
        except TypeError:
            pass
        else:
            raise AssertionError('it should not allow to get arguments')


def do_origin(x):
    x[0] += 1
    return x


def do_replace_without_origin(x):
    x[0] += 2
    return x


def do_replace_with_origin(x, __origin):
    __origin(x)
    x[0] += 3
    return x


class Test_class_ReplaceFunction:
    def test_01_replace_print(self):
        def other_print(*args, sep=' ', end='\n'):
            arg_list = [str(_) for _ in args]
            print_text = 'this is other print:' + str(sep).join(arg_list) + str(end)
            sys.stdout.write(print_text)
            return print_text

        replace_function(print, other_print)

        assert type(print) is ReplaceFunction
        assert print('a', 123, True, None, sep='-', end='~~') == 'this is other print:a-123-True-None~~'
        assert len(print.history) == 2
        assert print.index == 1

        replace_function(print, other_print)

        assert type(print) is ReplaceFunction
        assert print((1, 1), 3.3, [], sep='+', end='><') == 'this is other print:(1, 1)+3.3+[]><'
        assert len(print.history) == 3
        assert print.index == 2
        print.index = 1
        assert print.target.__name__ == 'other_print'

        restore_function(print)

        assert type(print).__name__ == 'builtin_function_or_method'
        assert print('b', -32, False, None, sep='!', end='<>') is None

        restore_function(print)

        assert type(print).__name__ == 'builtin_function_or_method'
        assert print('cfr', -3.2, [{}], sep='!', end='$%^&') is None

    def test_02_replace_function_with_origin(self):
        test_list = [1, 2, 3]
        do_origin(test_list)
        assert test_list[0] == 2
        assert test_list[1] == 2
        assert test_list[2] == 3

        test_list = [1, 2, 3]
        replace_function(do_origin, do_replace_without_origin)
        do_origin(test_list)
        assert test_list[0] == 3
        assert test_list[1] == 2
        assert test_list[2] == 3

        test_list = [1, 2, 3]
        replace_function(do_origin, do_replace_with_origin)
        do_origin(test_list)
        assert test_list[0] == 5
        assert test_list[1] == 2
        assert test_list[2] == 3
