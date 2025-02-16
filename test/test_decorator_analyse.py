#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : test_decorator_analyse
# Author        : Sun YiFan-Movoid
# Time          : 2025/2/16 18:18
# Description   : 
"""
from movoid_function import analyse_args_kw_value_from_function


def target1(a, /, b, c, d=4, e=5, *, f=6, g=7):
    return a, b, c, d, e, f, g


class Test_function_analyse_args_kw_value_from_function:
    def test_minimum(self):
        value = analyse_args_kw_value_from_function(target1, 1, 2, 3)
        assert value == {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, }

    def test_maximum(self):
        value = analyse_args_kw_value_from_function(target1, 11, 22, 33, 44, 55, g=88, f=77)
        assert value == {'a': 11, 'b': 22, 'c': 33, 'd': 44, 'e': 55, 'f': 77, 'g': 88, }

    def test_more_keyword(self):
        value = analyse_args_kw_value_from_function(target1, 11, b=22, c=33, d=44, e=55, g=88, f=77)
        assert value == {'a': 11, 'b': 22, 'c': 33, 'd': 44, 'e': 55, 'f': 77, 'g': 88, }

    def test_position_error(self):
        try:
            value = analyse_args_kw_value_from_function(target1, a=1)
        except TypeError as err:
            print(err)
        else:
            raise AssertionError('对positional only的参数传入keyword参数，没有报错')

    def test_lack_of_argument_error(self):
        try:
            value = analyse_args_kw_value_from_function(target1, 1, 2)
        except TypeError as err:
            print(err)
        else:
            raise AssertionError('传入的参数数量过少，没有报错')
