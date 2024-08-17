#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : function
# Author        : Sun YiFan-Movoid
# Time          : 2024/4/13 16:35
# Description   : 
"""
import inspect

from .decorator import adapt_call


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
            def empty_function(*arg, **kwarg):
                return None

            self._func = empty_function
        else:
            raise NameError(f'try to create a invalid function: {func}')
        self._args = args if args else ()
        self._kwargs = kwargs if kwargs else {}

    def __call__(self, *args, **kwargs):
        if args or kwargs:
            re_value = self._func(*args, **kwargs)
        else:
            re_value = self._func(*self._args, **self._kwargs)
        return re_value

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


class ReplaceFunction:
    def __init__(self, ori_func, tar_func):
        if isinstance(ori_func, ReplaceFunction):
            self._history = ori_func.history
        else:
            self._history = [ori_func]
        self._history.append(tar_func)
        self._index = -1
        self.use_last()

    def __call__(self, *args, **kwargs):
        kwargs_with_ori = {'__origin': self.origin, **kwargs}
        return adapt_call(self.target, args, kwargs_with_ori)

    def call(self, *args, **kwargs):
        return self.target(*args, **kwargs)

    @property
    def origin(self):
        return self._history[0]

    @property
    def target(self):
        return self._history[self._index]

    @property
    def last(self):
        return self._history[-1]

    @property
    def history(self) -> list:
        return self._history

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        value = int(value) % len(self._history)
        self._index = value

    def use_ori(self):
        self.index = 0
        return self

    def use_last(self):
        self.index = -1
        return self


def replace_function(ori_func, tar_func):
    if isinstance(ori_func, ReplaceFunction):
        ori = ori_func.origin
    else:
        ori = ori_func
    ori_package = inspect.getmodule(ori)
    func_name = ori.__name__
    setattr(ori_package, func_name, ReplaceFunction(ori_func, tar_func))


def restore_function(tar_func):
    if isinstance(tar_func, ReplaceFunction):
        ori_package = inspect.getmodule(tar_func.origin)
        func_name = tar_func.origin.__name__
        setattr(ori_package, func_name, tar_func.origin)
