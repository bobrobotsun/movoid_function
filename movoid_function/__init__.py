#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : __init__.py
# Author        : Sun YiFan-Movoid
# Time          : 2024/1/28 16:03
# Description   : 
"""

from .decorator import (wraps, wraps_kw, wraps_func,
                        wraps_ori, wraps_add_one, wraps_add_multi,
                        reset_function_default_value, analyse_args_value_from_function, adapt_call,
                        decorate_class_function_include, decorate_class_function_exclude)
from .function import Function, ReplaceFunction, replace_function, restore_function
from .type import check_parameters_type
