#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : test_function
# Author        : Sun YiFan-Movoid
# Time          : 2024/7/21 1:00
# Description   : 
"""

import pytest
from movoid_function import Function


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
