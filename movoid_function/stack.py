#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : stack
# Author        : Sun YiFan-Movoid
# Time          : 2025/11/26 15:33
# Description   : 
"""
import inspect
import math
import pathlib
import sys
import types
from typing import List, Tuple, Optional, Union

SKIP_MAX = 1_000_000
CALL = 50
DECORATOR = 50
DEBUG = 30
UI = 10
NO_SKIP = 0

NoInfo = 0
OnlyFunction = 2
NameFunction = 5
ModuleFunction = 8
PathFunction = 10


class StackFrame:
    """
    实际上这里是根据frame、module等信息来构建一个追溯得方案
    主要得目标是为了显示frame和log中得显示信息
    所以它包含了几种信息得存储方式
    1、记录一个frame，可以展示，也可以储存。匹配时，必须module、lineno都相等才算匹配成功
    2、记录一个module，这个module内和所有submodule的函数均被标记为待跳过项
    3、记录
    """

    def __init__(self, frame, level=DECORATOR, self_check_str='', encoding='utf8'):
        self._frame: Optional[types.FrameType] = None
        self._module: str = '__unknown__'
        self._module_list: List[str] = []
        self._file_path: Optional[pathlib.Path] = None
        self._file_str: str = ''
        self._lineno: Optional[int] = None
        self._func_name: str = ''
        self.self_check_str = self_check_str
        self.encoding = encoding
        if isinstance(level, int):
            self._level = level
        else:
            raise TypeError(f'level:{level}({type(level).__name__}) must be int')
        if isinstance(frame, StackFrame):
            self._frame = frame._frame
            self._module = frame._module
            self._module_list = frame._module_list
            self._file_path = frame._file_path
            self._file_str = frame._file_str
            self._lineno = frame._lineno
            self._func_name = frame._func_name
        elif inspect.isframe(frame):
            self._frame = frame
            if '__name__' in frame.f_globals:
                self._module = frame.f_globals.get('__name__', '__unknown__')
            else:
                self._module = '__unknown__'
                print('globals------------',frame.f_globals)
            self._module_list = self._module.split('.')
            self._file_path = pathlib.Path(frame.f_code.co_filename).absolute().resolve()
            self._lineno = frame.f_lineno
            self._func_name = frame.f_code.co_name
        elif inspect.ismodule(frame):
            self._file_path = pathlib.Path(frame.__file__).absolute().resolve()
            self._module = frame.__name__
            self._module_list = self._module.split('.')
        elif isinstance(frame, (tuple, list)):
            if 1 <= len(frame) <= 3:
                module = frame[0]
                if inspect.isframe(module):
                    self._frame = module
                    if '__name__' in module.f_globals:
                        self._module = module.f_globals.get('__name__', '__unknown__')
                    else:
                        self._module = '__unknown__'
                        print(module.f_globals)
                    self._module_list = self._module.split('.')
                    self._file_path = pathlib.Path(module.f_code.co_filename).absolute().resolve()
                    self._lineno = module.f_lineno
                    self._func_name = module.f_code.co_name
                elif isinstance(module, str):
                    self._module = module
                    self._module_list = self._module.split('.')
                elif inspect.ismodule(frame):
                    self._file_path = pathlib.Path(frame.__file__).absolute().resolve()
                    self._module = frame.__name__
                    self._module_list = self._module.split('.')
                else:
                    raise ValueError(f'module {module}({type(module).__name__}) should be module or str')
                if len(frame) >= 2:
                    self._lineno = int(frame[1])
                if len(frame) >= 3:
                    self._func_name = str(frame[2])
        else:
            raise TypeError(f'frame:{frame}({type(frame).__name__}) can not be parsed')

    def info(self, info_style=ModuleFunction):
        if info_style == ModuleFunction:
            return f'{self._module}{self.lineno_str}:{self._func_name}'
        elif info_style == NameFunction:
            return f'{self._module_list[-1]}{self.lineno_str}:{self._func_name}'
        elif info_style == OnlyFunction:
            return f'{self._func_name}'
        elif info_style == NoInfo:
            return ''
        elif info_style == PathFunction:
            return f'{self.file_full}{self.lineno_str}:{self._func_name}'
        else:
            raise ValueError(f'no level is {info_style},only accept level:{NoInfo} {OnlyFunction} {NameFunction} {ModuleFunction} {PathFunction}')

    @property
    def frame(self) -> types.FrameType:
        return self._frame

    @property
    def level(self):
        return self._level

    @property
    def file_full(self):
        if self._file_path is None:
            return self._file_str
        else:
            return str(self._file_path)

    @property
    def lineno_str(self):
        if self._lineno is None:
            return ''
        else:
            return f':{self._lineno}'

    @property
    def f_back(self) -> Optional['StackFrame']:
        if self._frame is None or self._frame.f_back is None:
            return None
        else:
            return StackFrame(self._frame.f_back, self.level)

    def match(self, other) -> Tuple[bool, bool]:
        if isinstance(other, StackFrame):
            level_bool = other._level >= self._level
            if other._lineno is not None:
                if self._lineno is not None:
                    return self._module == other._module and self._lineno == other._lineno, level_bool
                else:
                    return False, level_bool
            else:
                module_match = self.match_module(other)
                return module_match > 0, level_bool
        else:
            return self.match(StackFrame(other))

    def match_module(self, other) -> int:
        """
        纯粹考察module的关系，不考虑level
        :param other: 规则StackFrame
        :return: 2完全匹配，1子module，0不匹配
        """
        if isinstance(other, StackFrame):
            if other._module == '__main__':
                if self._module == '__main__':
                    return 2
                else:
                    return 1
            elif len(other._module_list) > len(self._module_list):
                return 0
            else:
                for i, other_module in enumerate(other._module_list):
                    self_module = self._module_list[i]
                    if self_module == other_module:
                        continue
                    else:
                        return 0
                else:
                    if len(other._module_list) == len(self._module_list):
                        return 2
                    else:
                        return 1
        else:
            return self.match_module(StackFrame(other))

    def to_str(self):
        list_str = f'["{self._module}"'
        if self._lineno is not None:
            list_str += f', {self._lineno}'
            if self._func_name is not None:
                list_str += f', {self._func_name}'
        list_str += f']'
        return f'StackFrame({list_str}, {self._level})'

    def __str__(self):
        return self.to_str()

    def __repr__(self):
        return self.to_str()

    def self_check(self):
        if self._file_path is not None and self._lineno is not None and self.self_check_str:
            with self._file_path.open('r', encoding=self.encoding) as f:
                for i in range(self._lineno - 1):
                    f.readline()
                target_str = f.readline().strip()
            assert target_str == self.self_check_str, f'{target_str} != {self.self_check_str}, please check {self._file_path}:{self._lineno} first.'


class Stack:
    ignore_list: List[StackFrame] = []

    def __init__(self):
        pass

    @property
    def lineno(self):
        return inspect.currentframe().f_back.f_lineno

    def __call__(self, frame, level=DECORATOR, self_check_str='', encoding='utf8'):
        return StackFrame(frame, level=level, self_check_str=self_check_str, encoding=encoding)

    def should_ignore(self, stack_frame: StackFrame, add_it=False):
        """
        判定某个函数是否属于
        :param stack_frame:
        :param add_it:
        :return:
        """
        for rule_i in self.ignore_list:
            info_bool, level_bool = stack_frame.match(rule_i)
            if info_bool:
                if level_bool:
                    print(True,stack_frame,rule_i)
                    return True
                else:
                    break
        if add_it:
            self.ignore_list.append(stack_frame)
        print(False,stack_frame,self.ignore_list)
        return False

    def this_file_lineno_should_ignore(self, lineno: int, ignore_level: int = DECORATOR, check_text: str = '', encoding: str = 'utf8'):
        stack_frame = self.get_frame(1, skip_ignore_level=SKIP_MAX)
        stack_frame._lineno = int(lineno)
        stack_frame._level = int(ignore_level)
        stack_frame.self_check_str = str(check_text)
        stack_frame.encoding = encoding
        self.should_ignore(stack_frame, add_it=True)

    def module_should_ignore(self, module, ignore_level: int = DECORATOR):
        self.should_ignore(StackFrame(module, level=ignore_level), add_it=True)

    def get_frame(self, stacklevel=None, skip_ignore_level=DECORATOR) -> StackFrame:
        """
        获取回退一定level后的栈的信息
        :param stacklevel: 后退栈的数量
        :param skip_ignore_level: 根据level来跳过ignore的list
        :return: 目标栈
        """
        stack_frame = StackFrame(sys._getframe(), skip_ignore_level)
        stacklevel = 0 if stacklevel is None else stacklevel
        for f_index in range(stacklevel + 1):
            stack_frame = stack_frame.f_back
            while True:
                if self.should_ignore(stack_frame):
                    stack_frame = stack_frame.f_back
                    if stack_frame is None:
                        raise ValueError('frame back to None')
                else:
                    break
            if stack_frame is None:
                raise ValueError('frame back to None')
        return stack_frame

    def get_frame_list(self, stacklevel=None, init_ignore_level=NO_SKIP, skip_ignore_level=DECORATOR, with_index=False) -> List[List[Union[StackFrame, int]]]:
        """
        获取自己的所有的之前的栈的frame的列表
        :param stacklevel: 是否需要额外再回退若干栈
        :param init_ignore_level: 初始跳过stack level的时候
        :param skip_ignore_level: 是否要跳过那些需要ignore的栈
        :param with_index: 是否在返回的列表里包含index信息
        :return: 全部栈列表[[栈，回追的栈序号]]
        """
        stacklevel = 0 if stacklevel is None else stacklevel
        stack_frame = self.get_frame(stacklevel=stacklevel + 1, skip_ignore_level=init_ignore_level)
        stack_frame._level = skip_ignore_level
        re_list = []
        index = 0
        while stack_frame is not None:
            if self.should_ignore(stack_frame):
                stack_frame = stack_frame.f_back
                index += 1
                continue
            else:
                re_list.append([stack_frame, index] if with_index else stack_frame)
                index += 1
                stack_frame = stack_frame.f_back
        return re_list

    def self_check(self):
        for i in self.ignore_list:
            i.self_check()


STACK = Stack()
