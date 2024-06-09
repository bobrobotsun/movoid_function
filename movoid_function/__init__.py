#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : __init__.py
# Author        : Sun YiFan-Movoid
# Time          : 2024/1/28 16:03
# Description   : 
"""
from .decorator import recover_signature_from_function as wraps
from .decorator import recover_signature_from_function_func as wraps_func
from .decorator import recover_signature_from_function_only_kwargs as wraps_kw
from .decorator import reset_function_default_value, analyse_args_value_from_function
from .type import check_parameters_type
from .function import Function, ReplaceFunction, replace_function
