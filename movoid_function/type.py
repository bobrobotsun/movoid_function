#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : type
# Author        : Sun YiFan-Movoid
# Time          : 2024/1/30 22:45
# Description   : 
"""

import json
import pathlib
import re
from abc import ABC, abstractmethod
from typing import Union, Any

from .check import NumberCheck, CheckFormula
from .decorator import recover_signature_from_function_func


class Type(ABC):
    def __init__(self, convert=False, **kwargs):
        self._convert = bool(convert)

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def check(self, check_target, convert=None) -> bool:
        pass

    @abstractmethod
    def _convert_function(self, check_target):
        pass

    def convert(self, convert_target, convert=None):
        should_convert = self._convert if convert is None else bool(convert)
        if should_convert:
            re_value = self._convert_function(convert_target)
        else:
            re_value = convert_target
        return re_value

    @property
    def annotation(self):
        return Any


class Bool(Type):
    def __init__(self, convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)

    def __repr__(self):
        return f'Bool(convert={self._convert})'

    def check(self, check_target, convert=None) -> bool:
        check_target = self.convert(check_target, convert)
        return isinstance(check_target, bool)

    def _convert_function(self, check_target) -> bool:
        return bool(check_target)

    @property
    def annotation(self):
        if self._convert:
            return Any
        else:
            return bool


class Int(Type):
    def __init__(self, limit='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._limit = CheckFormula(limit, NumberCheck)

    def __repr__(self):
        limit_text = f'limit={self._limit}, ' if self._limit._str_formula else ''
        return f'Int({limit_text}convert={self._convert})'

    def check(self, check_target, convert=None) -> bool:
        check_target = self.convert(check_target, convert)
        if isinstance(check_target, int):
            re_bool = self._limit.check(check_target)
        else:
            re_bool = False
        return re_bool

    def _convert_function(self, check_target) -> int:
        return int(check_target)

    @property
    def annotation(self):
        if self._convert:
            return Union[int, str]
        else:
            return int


class Float(Type):
    def __init__(self, limit='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._limit = CheckFormula(limit, NumberCheck)

    def __repr__(self):
        limit_text = f'limit={self._limit}, ' if self._limit._str_formula else ''
        return f'Float({limit_text}convert={self._convert})'

    def check(self, check_target, convert=None) -> bool:
        check_target = self.convert(check_target, convert)
        if isinstance(check_target, float):
            re_bool = self._limit.check(check_target)
        else:
            re_bool = False
        return re_bool

    def _convert_function(self, check_target) -> float:
        return float(check_target)

    @property
    def annotation(self):
        if self._convert:
            return Union[float, str]
        else:
            return float


class Number(Type):
    def __init__(self, limit='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._limit = CheckFormula(limit, NumberCheck)

    def __repr__(self):
        limit_text = f'limit={self._limit}, ' if self._limit._str_formula else ''
        return f'Number({limit_text}convert={self._convert})'

    def check(self, check_target, convert=None) -> bool:
        check_target = self.convert(check_target, convert)
        if isinstance(check_target, float) or isinstance(check_target, int):
            re_bool = self._limit.check(check_target)
        else:
            re_bool = False
        return re_bool

    def _convert_function(self, check_target) -> Union[int, float]:
        temp = float(check_target)
        if float(int(temp)) == temp:
            return int(temp)
        else:
            return temp

    @property
    def annotation(self):
        if self._convert:
            return Union[int, float, str]
        else:
            return Union[int, float]


class Str(Type):
    def __init__(self, char=None, length='', regex=None, convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._char = char
        self._length = CheckFormula(length, NumberCheck)
        self._regex = regex

    def __repr__(self):
        char_text = f'char={self._char}, ' if self._char else ''
        limit_text = f'length={self._length}, ' if self._length._str_formula else ''
        regex_text = f'regex={self._regex}, ' if self._regex else ''
        return f'Str({char_text}{limit_text}{regex_text}convert={self._convert})'

    def check(self, check_target, convert=None) -> bool:
        check_target = self.convert(check_target, convert)
        if isinstance(check_target, str):
            re_bool = True
            if self._char:
                re_bool = re_bool and all([_ in self._char for _ in check_target])
            re_bool = re_bool and self._length.check(len(check_target))
            if self._regex:
                re_bool = re_bool and bool(re.search(self._regex, check_target))
        else:
            re_bool = False
        return re_bool

    def _convert_function(self, check_target) -> str:
        return str(check_target)

    @property
    def annotation(self):
        return str


class List(Type):
    def __init__(self, length='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._length = CheckFormula(length, NumberCheck)

    def __repr__(self):
        length_text = f'length={self._length}, ' if self._length._str_formula else ''
        return f'List({length_text}convert={self._convert})'

    def check(self, check_target, convert=None) -> bool:
        check_target = self.convert(check_target, convert)
        if isinstance(check_target, list):
            re_bool = True
            re_bool = re_bool and self._length.check(len(check_target))
        else:
            re_bool = False
        return re_bool

    def _convert_function(self, check_target) -> list:
        if isinstance(check_target, str):
            check_target = json.loads(check_target)
        return list(check_target)

    @property
    def annotation(self):
        if self._convert:
            return Union[list, str]
        else:
            return list


class Tuple(Type):
    def __init__(self, length='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._length = CheckFormula(length, NumberCheck)

    def __repr__(self):
        length_text = f'length={self._length}, ' if self._length._str_formula else ''
        return f'Tuple({length_text}convert={self._convert})'

    def check(self, check_target, convert=None) -> bool:
        check_target = self.convert(check_target, convert)
        if isinstance(check_target, tuple):
            re_bool = True
            re_bool = re_bool and self._length.check(len(check_target))
        else:
            re_bool = False
        return re_bool

    def _convert_function(self, check_target) -> tuple:
        if isinstance(check_target, str):
            check_target = json.loads(check_target)
        return tuple(check_target)

    @property
    def annotation(self):
        if self._convert:
            return Union[tuple, str]
        else:
            return tuple


class Set(Type):
    def __init__(self, length='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._length = CheckFormula(length, NumberCheck)

    def __repr__(self):
        length_text = f'length={self._length}, ' if self._length._str_formula else ''
        return f'Set({length_text}convert={self._convert})'

    def check(self, check_target, convert=None) -> bool:
        check_target = self.convert(check_target, convert)
        if isinstance(check_target, set):
            re_bool = True
            re_bool = re_bool and self._length.check(len(check_target))
        else:
            re_bool = False
        return re_bool

    def _convert_function(self, check_target) -> set:
        if isinstance(check_target, str):
            check_target = json.loads(check_target)
        return set(check_target)

    @property
    def annotation(self):
        if self._convert:
            return Union[set, str]
        else:
            return set


class Dict(Type):
    def __init__(self, length='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._length = CheckFormula(length, NumberCheck)

    def __repr__(self):
        length_text = f'length={self._length}, ' if self._length._str_formula else ''
        return f'Dict({length_text}convert={self._convert})'

    def check(self, check_target, convert=None) -> bool:
        check_target = self.convert(check_target, convert)
        if isinstance(check_target, dict):
            re_bool = True
            re_bool = re_bool and self._length.check(len(check_target))
        else:
            re_bool = False
        return re_bool

    def _convert_function(self, check_target) -> dict:
        if isinstance(check_target, str):
            check_target = json.loads(check_target)
        return dict(check_target)

    @property
    def annotation(self):
        if self._convert:
            return Union[dict, str]
        else:
            return dict


class Path(Type):
    def __init__(self, should_exist=True, convert=False, **kwargs):
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

    def _convert_function(self, check_target):
        return str(check_target)

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


def check_parameters_type(convert=False, check_arguments=True, check_return=True):
    def dec(func):
        argument_annotation = {}
        return_annotation = {}
        change_annotation = {}
        for _i, _v in func.__annotations__.items():
            if _v in default_type:
                real_annotation = default_type[_v](convert=convert)
                change_annotation[_i] = _v
            elif isinstance(_v, Type):
                real_annotation = _v
                change_annotation[_i] = _v.annotation
            else:
                change_annotation[_i] = _v
                continue
            if _i == 'return':
                if check_return:
                    return_annotation[_i] = real_annotation
            else:
                if check_arguments:
                    argument_annotation[_i] = real_annotation
        func.__annotations__ = change_annotation

        @recover_signature_from_function_func(func)
        def wrapper(**kwargs):
            for _i2, _v2 in kwargs.items():
                if _i2 in argument_annotation:
                    _v3 = argument_annotation[_i2]
                    check_result = _v3.check(_v2)
                    if not check_result:
                        raise TypeError(f'{_i2} is {_v2}({type(_v2).__name__}),but it should be a {_v3}')
                    kwargs[_i2] = _v3.convert(_v2)
            re_value = func(**kwargs)
            if 'return' in return_annotation:
                _v3 = return_annotation['return']
                check_result = _v3.check(re_value)
                if not check_result:
                    raise TypeError(f'return value is {re_value}({type(re_value).__name__}),but it should be a {_v3}')
                re_value = _v3.convert(re_value)
            return re_value

        return wrapper

    return dec
