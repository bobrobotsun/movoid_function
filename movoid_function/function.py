#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : function
# Author        : Sun YiFan-Movoid
# Time          : 2024/4/13 16:35
# Description   : 
"""


def empty_function(*args, **kwargs):
    return None


class Function:
    def __init__(self, func=None, args=None, kwargs=None, empty_ok=True):
        self._func = None
        self._args = ()
        self._kwargs = {}
        if isinstance(func, (list, tuple)):
            self.init(*func, empty_ok=empty_ok)
        elif isinstance(func, dict):
            self.init(**func, empty_ok=empty_ok)
        else:
            self.init(func, args, kwargs, empty_ok=empty_ok)

    def init(self, func=None, args=None, kwargs=None, empty_ok=True):
        if callable(func):
            self._func = func
        elif empty_ok:
            self._func = empty_function
        else:
            raise NameError(f'try to create a invalid function: {func}')
        self._args = args if args else ()
        self._kwargs = kwargs if kwargs else {}

    def __call__(self, *args, **kwargs):
        if args or kwargs:
            self._func(*args, **kwargs)
        else:
            self._func(*self._args, **self._kwargs)

    @property
    def id(self):
        return id(self._func)

    @property
    def name(self):
        return self._func.__code__.co_name

    @property
    def file(self):
        return self._func.__code__.co_filename

    @property
    def lineno(self):
        return self._func.__code__.co_firstlineno
