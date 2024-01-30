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


class Type(ABC):
    def __init__(self, convert=False, **kwargs):
        self._convert = convert

    @abstractmethod
    def check(self, check_target) -> bool:
        pass

    @abstractmethod
    def _convert_function(self, check_target):
        pass

    @property
    def annotation(self):
        return Any


class TypeInt(Type):
    def __init__(self, limit='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._limit = CheckFormula(limit, NumberCheck)

    def check(self, check_target) -> bool:
        if self._convert:
            check_target = self._convert_function(check_target)
        return self._limit.check(check_target)

    def _convert_function(self, check_target) -> int:
        return int(check_target)

    @property
    def annotation(self):
        if self._convert:
            return Union[int, str]
        else:
            return int


class TypeFloat(Type):
    def __init__(self, limit='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._limit = CheckFormula(limit, NumberCheck)

    def check(self, check_target) -> bool:
        if self._convert:
            check_target = self._convert_function(check_target)
        return self._limit.check(check_target)

    def _convert_function(self, check_target) -> float:
        return float(check_target)

    @property
    def annotation(self):
        if self._convert:
            return Union[float, str]
        else:
            return float


class TypeNumber(Type):
    def __init__(self, limit='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._limit = CheckFormula(limit, NumberCheck)

    def check(self, check_target) -> bool:
        if self._convert:
            check_target = self._convert_function(check_target)
        return self._limit.check(check_target)

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


class TypeStr(Type):
    def __init__(self, char=None, length='', regex=None, convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._char = char
        self._length = CheckFormula(length, NumberCheck)
        self._regex = regex

    def check(self, check_target) -> bool:
        if self._convert:
            check_target = self._convert_function(check_target)
        re_bool = True
        if self._char:
            re_bool = re_bool and all([_ in self._char for _ in check_target])
        re_bool = re_bool and self._length.check(len(check_target))
        if self._regex:
            re_bool = re_bool and bool(re.search(self._regex, check_target))
        return re_bool

    def _convert_function(self, check_target) -> str:
        return str(check_target)

    @property
    def annotation(self):
        return str


class TypeList(Type):
    def __init__(self, length='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._length = CheckFormula(length, NumberCheck)

    def check(self, check_target) -> bool:
        if self._convert:
            check_target = self._convert_function(check_target)
        re_bool = True
        re_bool = re_bool and self._length.check(len(check_target))
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


class TypeDict(Type):
    def __init__(self, length='', convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)
        self._length = CheckFormula(length, NumberCheck)

    def check(self, check_target) -> bool:
        if self._convert:
            check_target = self._convert_function(check_target)
        re_bool = True
        re_bool = re_bool and self._length.check(len(check_target))
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


class TypePath(Type):
    def __init__(self, convert=False, **kwargs):
        super().__init__(convert=convert, **kwargs)

    def check(self, check_target) -> bool:
        if self._convert:
            check_target = self._convert_function(check_target)
        re_bool = True
        re_bool = re_bool and pathlib.Path(check_target).exists()
        return re_bool

    def _convert_function(self, check_target):
        return str(check_target)

    @property
    def annotation(self):
        return str
