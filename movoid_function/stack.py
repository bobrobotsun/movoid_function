#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : stack
# Author        : Sun YiFan-Movoid
# Time          : 2025/11/26 15:33
# Description   : 
"""
import inspect
import pathlib
import sys
import types
from typing import List


class StackInfo:
    ignore_list = []

    def __init__(self, func):
        if isinstance(func, StackInfo):
            self.func_name = func.func_name
            self.file_path = func.file_path
            self.start_line = func.start_line
        elif inspect.isframe(func):
            self.func_name = func.f_code.co_name
            self.file_path = func.f_code.co_filename
            self.start_line = func.f_lineno
        elif callable(func):
            self.func_name = func.__name__
            if hasattr(func, "__code__"):
                self.file_path = func.__code__.co_filename
                self.start_line = func.__code__.co_firstlineno
            else:
                self.file_path = "<builtin>"
                self.start_line = None
        elif isinstance(func, (tuple, list)):
            if 2 <= len(func) <= 3:
                self.file_path = func[0]
                self.start_line = func[1]
                if len(func) == 3:
                    self.func_name = func[2]
                else:
                    self.func_name = None
            else:
                raise ValueError('can not analyse list or tuple length is not 2/3')
        else:
            raise TypeError("func must be callable or list or tuple")

    def __eq__(self, other):
        if isinstance(other, StackInfo):
            return self.file_path == other.file_path and self.start_line == other.start_line
        else:
            return self == StackInfo(other)

    def __str__(self):
        return self.tostring()

    def __repr__(self):
        return f'StackInfo{self.tostring()}'

    def tostring(self):
        func_str = f'None' if self.func_name is None else f'"{self.func_name}"'
        return f'(r"{self.file_path}", {self.start_line}, {func_str})'

    @property
    def info(self):
        return self.file_path, self.start_line, self.func_name


class Stack:
    def __init__(self):
        self.ignore_list = []

    @property
    def lineno(self):
        return inspect.currentframe().f_back.f_lineno

    def __call__(self, func):
        return StackInfo(func)

    def should_ignore(self, func, add_it=False):
        """
        判定某个函数是否属于
        :param func:
        :param add_it:
        :return:
        """
        ignore_func = StackInfo(func)
        for func_i in self.ignore_list:
            if func_i == ignore_func:
                return True
        else:
            if add_it:
                self.ignore_list.append(ignore_func)
            return False

    def file_should_ignore(self, file_path: str, line_content: str, strip: bool = True, encoding: str = 'utf8'):  # TODO:这里没有办法正确区分缩进情况，可能未来可以进行处理
        """
        将目标文件中整段文字匹配的行纳入ignore list中。
        如果只想要把本文件进行处理，可以直接输入__file__作为参数
        :param file_path: 文件名，建议__file__
        :param line_content: 目标行全文
        :param strip: 是否strip所有的空格和tab
        :param encoding: 文件编码，默认UTF8
        """
        this_file = pathlib.Path(file_path).absolute().resolve()
        with this_file.open('r', encoding=encoding) as f:
            for line_index, line in enumerate(f.readlines()):
                line_strip = line.strip() if strip else line.strip('\n')
                if line_strip == line_content:
                    self.should_ignore([str(this_file), line_index + 1], add_it=True)

    def dec_ignore(self, func):
        """
        装饰器，用来将目标函数加入ignore列表
        """
        self.should_ignore(func, add_it=True)
        return func

    def get_simple_frame_info(self, stacklevel=None, skip_ignore=True):
        """
        根据stacklevel的数值，追溯到目标frame，并显示简易信息。会忽略所有需要ignore的信息
        :param stacklevel: 向前追溯的stack层数
        :param skip_ignore: 是否跳过ignore的信息
        :return: 目标栈的 文件名、行号、函数名
        """
        frame = sys._getframe()
        stacklevel = 0 if stacklevel is None else stacklevel
        for f_index in range(stacklevel + 1):
            frame = frame.f_back
            while skip_ignore:
                if self.should_ignore(frame):
                    frame = frame.f_back
                    if frame is None:
                        raise ValueError('frame back to None')
                else:
                    break
            if frame is None:
                raise ValueError('frame back to None')
        return StackInfo(frame).info

    def get_frame(self, stacklevel=None, skip_ignore=True) -> types.FrameType:
        """
        获取回退一定level后的栈的信息
        :param stacklevel: 后退栈的数量
        :param skip_ignore: 是否跳过那些需要ignore的栈
        :return: 目标栈
        """
        frame = sys._getframe().f_back
        stacklevel = 0 if stacklevel is None else stacklevel
        for f_index in range(stacklevel):
            while skip_ignore:
                if self.should_ignore(frame):
                    frame = frame.f_back
                    if frame is None:
                        raise ValueError('frame back to None')
                else:
                    break
            frame = frame.f_back
            if frame is None:
                raise ValueError('frame back to None')
        return frame

    def get_frame_list(self, skip_ignore=True) -> List[types.FrameType]:
        """
        获取自己的所有的之前的栈的frame的列表
        :param skip_ignore: 是否要跳过那些需要ignore的栈
        :return: 全部栈列表
        """
        frame = sys._getframe().f_back
        re_list = []
        while frame is not None:
            if skip_ignore and self.should_ignore(frame):
                frame = frame.f_back
                continue
            else:
                re_list.append(frame)
                frame = frame.f_back
        return re_list


STACK = Stack()
