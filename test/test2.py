#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : test2
# Author        : Sun YiFan-Movoid
# Time          : 2024/6/9 14:06
# Description   : 
"""
from movoid_function import wraps
from movoid_function.decorator import analyse_args_value_from_function


def dec(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(args, kwargs)
        arg_value = analyse_args_value_from_function(func, *args, **kwargs)
        print(arg_value)

    return wrapper


@dec
def test1(a, *args, b=1, **kwargs):
    pass


test1(a=123, ss=123)
