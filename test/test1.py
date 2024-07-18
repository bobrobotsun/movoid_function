#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : test1
# Author        : Sun YiFan-Movoid
# Time          : 2024/6/9 14:01
# Description   : 
"""
import builtins
import inspect
import sys

from test2 import test2_do_print, exchange
from movoid_function.function import replace_function, ReplaceFunction


def test_print(*args, sep=' ', end='\n', file=None, flush=True):
    temp_args = [str(_) for _ in args]
    temp_str = sep.join(temp_args) + str(file) + str(flush) + end
    sys.stdout.write(temp_str)


print(inspect.Signature.from_callable(print))
replace_function(print, test_print)
# builtins.print = test_print
# exchange(builtins.print, test_print)
# builtins.print = ReplaceFunction(builtins.print, test_print)
print('all')
print(inspect.Signature.from_callable(print))
