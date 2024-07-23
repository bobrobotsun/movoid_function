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


class Test_class_ReplaceFunction:
    def test_01_replace_builtin_function(self):
        def other_print(*args, sep=' ', end='\n'):
            arg_list = [str(_) for _ in args]
            print_text = 'this is other print:' + str(sep).join(arg_list) + str(end)
            sys.stdout.write(print_text)
            return print_text

        replace_function(print, other_print)

        assert type(print) is ReplaceFunction
        assert print('a', 123, True, None, sep='-', end='~~') == 'this is other print:a-123-True-None~~'

        restore_function(print)

        assert type(print).__name__ == 'builtin_function_or_method'
        assert print('b', -32, False, None, sep='!', end='<>') is None

    def test_02_replace_builtin_function_cross_file(self):
        def other_print(*args, sep=' ', end='\n'):
            arg_list = [str(_) for _ in args]
            print_text = 'this is test print:' + str(sep).join(arg_list) + str(end)
            sys.stdout.write(print_text)
            return print_text

        replace_function(print, other_print)
