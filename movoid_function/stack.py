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

DECORATOR = 50
DEBUG = 30
UI = 10
NO_SKIP = 0


class StackInfo:
    ignore_list = []

    def __init__(self, func, level=DECORATOR):
        if isinstance(level, int):
            self.level = level
        else:
            raise TypeError(f'level:{level}({type(level).__name__}) must be int')
        if isinstance(func, StackInfo):
            self.func_name = func.func_name
            self.file_path = func.file_path
            self.start_line = func.start_line
        elif inspect.isframe(func):
            self.func_name = func.f_code.co_name
            self.file_path = pathlib.Path(func.f_code.co_filename).absolute().resolve()
            self.start_line = func.f_lineno
        elif callable(func):
            self.func_name = func.__name__
            if hasattr(func, "__code__"):
                self.file_path = pathlib.Path(func.__code__.co_filename).absolute().resolve()
                self.start_line = func.__code__.co_firstlineno
            else:
                self.file_path = "<builtin>"
                self.start_line = None
        elif isinstance(func, (tuple, list)):
            if 1 <= len(func) <= 3:
                self.file_path = pathlib.Path(func[0]).absolute().resolve()
                if len(func) >= 2:
                    self.start_line = func[1]
                else:
                    self.start_line = None
                if len(func) == 3:
                    self.func_name = func[2]
                else:
                    self.func_name = None
            else:
                raise ValueError('can not analyse list or tuple length is not 1/2/3')
        else:
            raise TypeError("func must be callable or list or tuple")

    def __eq__(self, other):
        if isinstance(other, StackInfo):
            return self.file_path == other.file_path and (other.start_line is None or self.start_line == other.start_line)
        else:
            return self == StackInfo(other)

    def __str__(self):
        return self.tostring()

    def __repr__(self):
        return f'StackInfo({self.tostring()}, {self.level})'

    def tostring(self):
        func_str = f'None' if self.func_name is None else f'"{self.func_name}"'
        return f'(r"{self.file_path}", {self.start_line}, {func_str})'

    def match(self, taget_stack_info: 'StackInfo'):
        return self == taget_stack_info, self.level >= taget_stack_info.level  # 一般用于将新生成的stack.match（记录好的stack），只有新生成的level足够高才会match

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

    def should_ignore(self, stack_info: StackInfo, add_it=False):
        """
        判定某个函数是否属于
        :param stack_info:
        :param add_it:
        :return:
        """
        for func_i in self.ignore_list:
            info_bool, level_bool = stack_info.match(func_i)
            if info_bool:
                if level_bool:
                    return True
                else:
                    break
        if add_it:
            self.ignore_list.append(stack_info)
            return False

    def file_should_ignore(self, file_path: str, line_content: str, ignore_level: int = DECORATOR, strip: bool = True, encoding: str = 'utf8', check_count=None):  # TODO:这里没有办法正确区分缩进情况，可能未来可以进行处理
        """
        将目标文件中整段文字匹配的行纳入ignore list中。
        如果只想要把本文件进行处理，可以直接输入__file__作为参数
        :param file_path: 文件名，建议__file__
        :param line_content: 目标行全文，如果输入None，那么会尝试将全文件纳入ignore list
        :param ignore_level: 相应的忽略等级，默认是装饰器级别
        :param check_count: 是否检查数量，如果需要检查，那么输入一个数字
        :param strip: 是否strip所有的空格和tab
        :param encoding: 文件编码，默认UTF8
        """
        this_file = pathlib.Path(file_path).absolute().resolve()
        count = 0
        if line_content is None:
            count += 1
            stack_info = StackInfo([str(this_file)], level=ignore_level)
            self.should_ignore(stack_info, add_it=True)
        else:
            with this_file.open('r', encoding=encoding) as f:
                for line_index, line in enumerate(f.readlines()):
                    line_strip = line.strip() if strip else line.strip('\n')
                    if line_strip == line_content:
                        count += 1
                        stack_info = StackInfo([str(this_file), line_index + 1], level=ignore_level)
                        self.should_ignore(stack_info, add_it=True)
        if check_count is not None and count != check_count:
            raise ValueError(f'count is {count} which should be {check_count}')

    def get_simple_frame_info(self, stacklevel=None, skip_ignore_level=DECORATOR):
        """
        根据stacklevel的数值，追溯到目标frame，并显示简易信息。会忽略所有需要ignore的信息
        :param stacklevel: 向前追溯的stack层数
        :param skip_ignore_level: 是否跳过ignore的信息
        :return: 目标栈的 文件名、行号、函数名
        """
        frame = sys._getframe()
        stacklevel = 0 if stacklevel is None else stacklevel
        for f_index in range(stacklevel + 1):
            frame = frame.f_back
            while True:
                stack_info = StackInfo(frame, level=skip_ignore_level)
                if self.should_ignore(stack_info):
                    frame = frame.f_back
                    if frame is None:
                        raise ValueError('frame back to None')
                else:
                    break
            if frame is None:
                raise ValueError('frame back to None')
        return StackInfo(frame).info

    def get_frame(self, stacklevel=None, skip_ignore_level=DECORATOR) -> types.FrameType:
        """
        获取回退一定level后的栈的信息
        :param stacklevel: 后退栈的数量
        :param skip_ignore_level: 根据level来跳过ignore的list
        :return: 目标栈
        """
        frame = sys._getframe()
        stacklevel = 0 if stacklevel is None else stacklevel
        for f_index in range(stacklevel + 1):
            frame = frame.f_back
            while True:
                stack_info = StackInfo(frame, level=skip_ignore_level)
                if self.should_ignore(stack_info):
                    frame = frame.f_back
                    if frame is None:
                        raise ValueError('frame back to None')
                else:
                    break
            if frame is None:
                raise ValueError('frame back to None')
        return frame

    def get_frame_list(self, stacklevel=None, init_ignore_level=NO_SKIP, skip_ignore_level=DECORATOR, with_index=False) -> List[types.FrameType]:
        """
        获取自己的所有的之前的栈的frame的列表
        :param stacklevel: 是否需要额外再回退若干栈
        :param init_ignore_level: 初始跳过stack level的时候
        :param skip_ignore_level: 是否要跳过那些需要ignore的栈
        :param with_index: 是否在返回的列表里包含index信息
        :return: 全部栈列表
        """
        stacklevel = 0 if stacklevel is None else stacklevel
        frame = self.get_frame(stacklevel=stacklevel + 1, skip_ignore_level=init_ignore_level)
        re_list = []
        index = 0
        while frame is not None:
            stack_info = StackInfo(frame, level=skip_ignore_level)
            if self.should_ignore(stack_info):
                frame = frame.f_back
                index += 1
                continue
            else:
                re_list.append([frame, index] if with_index else frame)
                index += 1
                frame = frame.f_back
        return re_list


STACK = Stack()
