#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : function
# Author        : Sun YiFan-Movoid
# Time          : 2024/4/13 16:35
# Description   : 
"""
import inspect

from .stack import STACK
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
    def __init__(self, ori_func, tar_func, setup=None, teardown=None):
        if isinstance(ori_func, ReplaceFunction):
            self._history = ori_func.history
            self._setup = ori_func._setup
            self._teardown = ori_func._teardown
        else:
            self._history = [ori_func]
            self._setup = [None]
            self._teardown = [None]
        self._history.append(tar_func)
        if isinstance(setup, int):
            real_setup = setup % (len(self._history) - 1)
        else:
            real_setup = None
        self._setup.append(real_setup)
        if isinstance(teardown, int):
            real_teardown = teardown % (len(self._history) - 1)
        else:
            real_teardown = None
        self._teardown.append(real_teardown)
        self._index = -1
        self._setup_return = None
        self._teardown_return = None
        self._main_return = None
        self._ori_count = 0
        self.use_last()

    def __call__(self, *args, **kwargs):
        return self.call()(*args, **kwargs)

    def call(self, index=None, refresh_return=True):
        index = index % len(self._history) if isinstance(index, int) else self._index
        refresh_return = refresh_return if isinstance(refresh_return, bool) else True

        def wrapper(*args, **kwargs):
            if self._setup[index] is not None:
                _setup_return = self.call(self._setup[index], False)(*args, **kwargs)
                if refresh_return:
                    self._setup_return = _setup_return
            _main_return = adapt_call(self._history[index], args, kwargs)
            if refresh_return:
                self._main_return = _main_return
            if self._teardown[index] is not None:
                _teardown_return = self.call(self._teardown[index], False)(*args, **kwargs)
                if refresh_return:
                    self._teardown_return = _teardown_return
            return _main_return

        return wrapper

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

    @property
    def main_return(self):
        return self._main_return

    @property
    def setup_return(self):
        return self._setup_return

    @property
    def teardown_return(self):
        return self._teardown_return

    def use_ori(self):
        self.index = 0
        return self

    def use_last(self):
        self.index = -1
        return self

    def multi_use_ori(self):
        self._ori_count += 1
        self.index = 0
        return self

    def multi_use_last(self):
        self._ori_count -= 1
        self._ori_count = max(0, self._ori_count)
        if self._ori_count == 0:
            self.index = -1
        return self


def replace_function(ori_func, tar_func, setup=None, teardown=None):
    """
    将固有的函数替换为目标函数，一般是用于替换builtin的函数，或者一些包的直接定义的函数
    :param ori_func: 原始函数，直接传入就可以了，比如说直接传print
    :param tar_func: 代替用的函数，未来在使用的过程中，就会使用这个函数生效
    :param setup: 生效的时候，需不需要在执行前，执行一个被替换的函数，如果需要则建议输入0（原始函数）、-1（最后赋予的函数）进行代替
    :param teardown: 生效的时候，需不需要在执行完毕后，执行一个被替换的函数，如果需要则建议输入0（原始函数）、-1（最后赋予的函数）进行代替
    :return: 无
    """
    if isinstance(ori_func, ReplaceFunction):
        ori = ori_func.origin
    else:
        ori = ori_func
    ori_package = inspect.getmodule(ori)
    func_name = ori.__name__
    setattr(ori_package, func_name, ReplaceFunction(ori_func, tar_func, setup=setup, teardown=teardown))


def restore_function(tar_func):
    if isinstance(tar_func, ReplaceFunction):
        ori_package = inspect.getmodule(tar_func.origin)
        func_name = tar_func.origin.__name__
        setattr(ori_package, func_name, tar_func.origin)


STACK.this_file_lineno_should_ignore(42, check_text='re_value = self._func(*args, **kwargs)')
STACK.this_file_lineno_should_ignore(44, check_text='re_value = self._func(*self._args, **self._kwargs)')
STACK.this_file_lineno_should_ignore(93, check_text='return self.call()(*args, **kwargs)')
STACK.this_file_lineno_should_ignore(101, check_text='_setup_return = self.call(self._setup[index], False)(*args, **kwargs)')
STACK.this_file_lineno_should_ignore(104, check_text='_main_return = adapt_call(self._history[index], args, kwargs)')
STACK.this_file_lineno_should_ignore(108, check_text='_teardown_return = self.call(self._teardown[index], False)(*args, **kwargs)')
