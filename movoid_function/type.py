#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : type
# Author        : Sun YiFan-Movoid
# Time          : 2024/1/30 22:45
# Description   : 
"""

import pathlib
import re
import traceback
import typing
from abc import ABC, abstractmethod

from .check import NumberCheck, CheckFormula
from .decorator import wraps_func


class Type(ABC):
    def __init__(self, convert=False, **kwargs):
        self._convert = bool(convert)

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def convert_function(self, check_target) -> object:
        pass

    @abstractmethod
    def check_function(self, check_target) -> typing.List[str]:
        pass

    def check(self, check_target, convert=None):
        try:
            check_value = self.convert(check_target, convert)
        except:
            re_bool = False
            re_value = f'convert failed:\n{traceback.format_exc()}'
        else:
            fail_str = self.check_function(check_value)
            re_bool = len(fail_str) == 0
            re_value = check_value if re_bool else fail_str
        return re_bool, re_value

    def convert(self, convert_target, convert=None):
        should_convert = self._convert if convert is None else bool(convert)
        if should_convert:
            re_value = self.convert_function(convert_target)
        else:
            re_value = convert_target
        return re_value

    @property
    def annotation(self):
        return typing.Any


class Bool(Type):
    def __init__(self, convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)

    def __repr__(self):
        return f'Bool(convert={self._convert})'

    def convert_function(self, check_target) -> bool:
        if isinstance(check_target, str):
            if check_target.lower() in ('true', 'yes'):
                re_value = True
            elif check_target.lower() in ('false', 'no'):
                re_value = False
            else:
                raise ValueError(f'we do not know what is <{check_target}> for bool.')
        else:
            re_value = bool(check_target)
        return re_value

    def check_function(self, check_target) -> typing.List[str]:
        fail_str: typing.List[str] = []
        if not isinstance(check_target, bool):
            fail_str.append(f'{check_target} is {type(check_target).__name__} not bool')
        return fail_str

    @property
    def annotation(self):
        if self._convert:
            return typing.Any
        else:
            return bool


class Int(Type):
    def __init__(self, limit='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._limit = CheckFormula(limit, NumberCheck)

    def __repr__(self):
        limit_text = f'limit={self._limit}, ' if self._limit.formula else ''
        return f'Int({limit_text}convert={self._convert})'

    def convert_function(self, check_target) -> int:
        return int(check_target)

    def check_function(self, check_target) -> typing.List[str]:
        fail_str: typing.List[str] = []
        if isinstance(check_target, int):
            if not self._limit.check(check_target):
                fail_str.append(f'{check_target} did not match: {self._limit.show_all_step()}')
        else:
            fail_str.append(f'{check_target} is {type(check_target).__name__} not int')
        return fail_str

    @property
    def annotation(self):
        if self._convert:
            return typing.Union[int, str]
        else:
            return int


class Float(Type):
    def __init__(self, limit='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._limit = CheckFormula(limit, NumberCheck)

    def __repr__(self):
        limit_text = f'limit={self._limit}, ' if self._limit.formula else ''
        return f'Float({limit_text}convert={self._convert})'

    def convert_function(self, check_target) -> float:
        return float(check_target)

    def check_function(self, check_target) -> typing.List[str]:
        fail_str: typing.List[str] = []
        if isinstance(check_target, float):
            if not self._limit.check(check_target):
                fail_str.append(f'{check_target} did not match: {self._limit.show_all_step()}')
        else:
            fail_str.append(f'{check_target} is {type(check_target).__name__} not float')
        return fail_str

    @property
    def annotation(self):
        if self._convert:
            return typing.Union[float, str]
        else:
            return float


class Number(Type):
    def __init__(self, limit='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._limit = CheckFormula(limit, NumberCheck)

    def __repr__(self):
        limit_text = f'limit={self._limit}, ' if self._limit.formula else ''
        return f'Number({limit_text}convert={self._convert})'

    def convert_function(self, check_target) -> typing.Union[int, float]:
        temp = float(check_target)
        if float(int(temp)) == temp:
            return int(temp)
        else:
            return temp

    def check_function(self, check_target) -> typing.List[str]:
        fail_str: typing.List[str] = []
        if isinstance(check_target, (int, float)):
            if not self._limit.check(check_target):
                fail_str.append(f'{check_target} did not match: {self._limit.show_all_step()}')
        else:
            fail_str.append(f'{check_target} is {type(check_target).__name__} not number')
        return fail_str

    @property
    def annotation(self):
        if self._convert:
            return typing.Union[int, float, str]
        else:
            return typing.Union[int, float]


class Str(Type):
    def __init__(self, char=None, length='', regex=None, convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._char = char
        self._length = CheckFormula(length, NumberCheck)
        self._regex = regex

    def __repr__(self):
        char_text = f'char={self._char}, ' if self._char else ''
        limit_text = f'length={self._length}, ' if self._length.formula else ''
        regex_text = f'regex={self._regex}, ' if self._regex else ''
        return f'Str({char_text}{limit_text}{regex_text}convert={self._convert})'

    def convert_function(self, check_target) -> str:
        return str(check_target)

    def check_function(self, check_target) -> typing.List[str]:
        fail_str: typing.List[str] = []
        if isinstance(check_target, str):
            if self._char:
                char_error = [[_i, _v] for _i, _v in enumerate(check_target) if _v not in self._char]
                if char_error:
                    fail_str.append(f'{check_target} contain char more than <{self._char}>:{char_error}')
            if not self._length.check(len(check_target)):
                fail_str.append(f'{len(check_target)} length of {check_target} did not match: {self._length.show_all_step()}')
            if self._regex:
                if not bool(re.search(self._regex, check_target)):
                    fail_str.append(f'{check_target} does not meet rule {self._regex}')
        else:
            fail_str.append(f'{check_target} is {type(check_target).__name__} not str')
        return fail_str

    @property
    def annotation(self):
        return str


class List(Type):
    def __init__(self, length='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._length = CheckFormula(length, NumberCheck)

    def __repr__(self):
        length_text = f'length={self._length}, ' if self._length.formula else ''
        return f'List({length_text}convert={self._convert})'

    def convert_function(self, check_target) -> list:
        if isinstance(check_target, str):
            check_target = eval(check_target)
        return list(check_target)

    def check_function(self, check_target) -> typing.List[str]:
        fail_str: typing.List[str] = []
        if isinstance(check_target, str):
            if not self._length.check(len(check_target)):
                fail_str.append(f'{len(check_target)} length of {check_target} did not match: {self._length.show_all_step()}')
        else:
            fail_str.append(f'{check_target} is {type(check_target).__name__} not list')
        return fail_str

    def check(self, check_target, convert=None) -> bool:
        check_target = self.convert(check_target, convert)
        if isinstance(check_target, list):
            re_bool = True
            re_bool = re_bool and self._length.check(len(check_target))
        else:
            re_bool = False
        return re_bool

    @property
    def annotation(self):
        if self._convert:
            return typing.Union[list, str]
        else:
            return list


class Tuple(Type):
    def __init__(self, length='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._length = CheckFormula(length, NumberCheck)

    def __repr__(self):
        length_text = f'length={self._length}, ' if self._length.formula else ''
        return f'Tuple({length_text}convert={self._convert})'

    def convert_function(self, check_target) -> tuple:
        if isinstance(check_target, str):
            check_target = eval(check_target)
        return tuple(check_target)

    def check_function(self, check_target) -> typing.List[str]:
        fail_str: typing.List[str] = []
        if isinstance(check_target, str):
            if not self._length.check(len(check_target)):
                fail_str.append(f'{len(check_target)} length of {check_target} did not match: {self._length.show_all_step()}')
        else:
            fail_str.append(f'{check_target} is {type(check_target).__name__} not tuple')
        return fail_str

    @property
    def annotation(self):
        if self._convert:
            return typing.Union[tuple, str]
        else:
            return tuple


class Set(Type):
    def __init__(self, length='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._length = CheckFormula(length, NumberCheck)

    def __repr__(self):
        length_text = f'length={self._length}, ' if self._length.formula else ''
        return f'Set({length_text}convert={self._convert})'

    def convert_function(self, check_target) -> set:
        if isinstance(check_target, str):
            check_target = eval(check_target)
        return set(check_target)

    def check_function(self, check_target) -> typing.List[str]:
        fail_str: typing.List[str] = []
        if isinstance(check_target, str):
            if not self._length.check(len(check_target)):
                fail_str.append(f'{len(check_target)} length of {check_target} did not match: {self._length.show_all_step()}')
        else:
            fail_str.append(f'{check_target} is {type(check_target).__name__} not set')
        return fail_str

    @property
    def annotation(self):
        if self._convert:
            return typing.Union[set, str]
        else:
            return set


class Dict(Type):
    def __init__(self, length='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._length = CheckFormula(length, NumberCheck)

    def __repr__(self):
        length_text = f'length={self._length}, ' if self._length.formula else ''
        return f'Dict({length_text}convert={self._convert})'

    def convert_function(self, check_target) -> dict:
        if isinstance(check_target, str):
            check_target = eval(check_target)
        return dict(check_target)

    def check_function(self, check_target) -> typing.List[str]:
        fail_str: typing.List[str] = []
        if isinstance(check_target, str):
            if not self._length.check(len(check_target)):
                fail_str.append(f'{len(check_target)} length of {check_target} did not match: {self._length.show_all_step()}')
        else:
            fail_str.append(f'{check_target} is {type(check_target).__name__} not dict')
        return fail_str

    @property
    def annotation(self):
        if self._convert:
            return typing.Union[dict, str]
        else:
            return dict


class Path(Type):
    def __init__(self, should_exist=False, convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._should_exist = should_exist

    def __repr__(self):
        return f'Path(convert={self._convert})'

    def check(self, check_target, convert=None) -> bool:
        check_target = self.convert(check_target, convert)
        if isinstance(check_target, str):
            try:
                tar_path = pathlib.Path(check_target)
                if self._should_exist:
                    re_bool = tar_path.exists()
                else:
                    re_bool = True
            except:
                re_bool = False
        else:
            re_bool = False
        return re_bool

    def convert_function(self, check_target):
        return str(check_target)

    def check_function(self, check_target) -> typing.List[str]:
        fail_str: typing.List[str] = []
        if isinstance(check_target, str):
            try:
                tar_path = pathlib.Path(check_target)
                if self._should_exist and not tar_path.exists():
                    fail_str.append(f'{check_target} does not exists.')
            except:
                fail_str.append(f'{check_target} is not a valid path.')
        else:
            fail_str.append(f'{check_target} is {type(check_target).__name__} not path')
        return fail_str

    @property
    def annotation(self):
        return str


default_type = {
    bool: Bool,
    str: Str,
    int: Int,
    float: Float,
    list: List,
    set: Set,
    tuple: Tuple,
    dict: Dict,
}


def convert_type(target_type, **kwargs):
    if isinstance(target_type, Type):
        return target_type
    elif target_type in default_type:
        return default_type[target_type](**kwargs)
    else:
        return None


def check_parameters_type(convert=False, check_arguments=True, check_return=True):
    def dec(func):
        argument_annotation = {}
        return_annotation = {}
        change_annotation = {}
        for _i, _v in func.__annotations__.items():
            _v_convert = convert_type(_v)
            if _v is None:
                continue
            else:
                real_annotation = _v_convert
                change_annotation[_i] = _v_convert.annotation
            if _i == 'return':
                if check_return:
                    return_annotation[_i] = real_annotation
            else:
                if check_arguments:
                    argument_annotation[_i] = real_annotation
        func.__annotations__ = change_annotation

        @wraps_func(func)
        def wrapper(kwargs):
            for _i2, _v2 in kwargs.items():
                if _i2 in argument_annotation:
                    _v3 = argument_annotation[_i2]
                    _bool, _value = _v3.check(_v2, convert=convert)
                    if not _bool:
                        raise TypeError('\n'.join(_value))
                    kwargs[_i2] = _value
            re_value = func(**kwargs)
            if 'return' in return_annotation:
                _v3 = return_annotation['return']
                _bool, _value = _v3.check(re_value, convert=convert)
                if not _bool:
                    raise TypeError('\n'.join(_value))
                re_value = _value
            return re_value

        return wrapper

    return dec
