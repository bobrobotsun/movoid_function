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
from movoid_function.decorator import adapt_call


# def dec(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         print(args, kwargs)
#         arg_value = analyse_args_value_from_function(func, *args, **kwargs)
#         print(arg_value)
#
#     return wrapper


# @dec
# def test1(a, *, b, **kwargs):
#     pass


# test1(a=123, b=1233, ss=123)

def test(a1, a2, a3, a4, a5, a6):
    print(a1, a2, a3, a4, a5, a6)
    return a1


save_arg = []
save_kwarg = {}


def dec(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global save_arg, save_kwarg
        save_arg = args
        save_kwarg = kwargs
        print(args, kwargs)
        return func(*args, **kwargs)

    return wrapper


@dec
def dotest(a1, a2, a3, a4, **kwargs):
    return 2


dotest(1, 2, 3, a5=4, a4=5, a6=6)

re_value = adapt_call(test, [], {"a1": 123, "a6": 321}, dotest, save_arg, save_kwarg)
print(re_value)
