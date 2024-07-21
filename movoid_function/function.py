#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : function
# Author        : Sun YiFan-Movoid
# Time          : 2024/4/13 16:35
# Description   : 
"""
import inspect


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
        self._ori = ori_func
        self._tar = tar_func
        self._now = tar_func
        self.use_tar()

    def __call__(self, *args, **kwargs):
        return self._now(*args, **kwargs)

    def _call(self, *args, **kwargs):
        return self._now(*args, **kwargs)

    @property
    def origin(self):
        return self._ori

    @property
    def target(self):
        return self._tar

    def use_ori(self):
        self._now = self._ori

    def use_tar(self):
        self._now = self._tar


def replace_function(ori_func, tar_func):
    ori_package = inspect.getmodule(ori_func)
    func_name = ori_func.__name__
    setattr(ori_package, func_name, ReplaceFunction(ori_func, tar_func))


def restore_function(tar_func):
    ori_package = inspect.getmodule(tar_func.origin)
    func_name = tar_func.origin.__name__
    setattr(ori_package, func_name, tar_func.origin)
