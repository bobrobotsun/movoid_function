#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : test_function
# Author        : Sun YiFan-Movoid
# Time          : 2024/7/21 1:00
# Description   : 
"""

import pytest


class TestFunction:
    def setup_class(self):
        print('setup class')


    def test_class_function(self):
        print(1)