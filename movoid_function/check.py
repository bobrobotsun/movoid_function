#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : check
# Author        : Sun YiFan-Movoid
# Time          : 2024/1/30 22:45
# Description   : 
"""
from copy import deepcopy
from typing import Union


class NumberCheck:
    print = print

    def __init__(self, formula: str):
        self._formula = formula.strip(' ')
        self._not = False
        self._range = False
        self._left = None
        self._left_equal = False
        self._right = None
        self._right_equal = False
        self._middle = None
        self._analyse()

    def __repr__(self):
        return f'NumberCheck({self._formula})'

    def _analyse(self):
        now_formula = self._formula
        while now_formula.startswith('!'):
            now_formula = now_formula[1:]
            self._not = not self._not
        if '>' in now_formula:
            self._analyse_range(*now_formula.split('>', 1), reverse=True)
        elif '<' in now_formula:
            self._analyse_range(*now_formula.split('<', 1), reverse=False)
        else:
            try:
                self._middle = float(now_formula)
            except ValueError:
                raise ValueError(f'{now_formula} is not a number')

    def _analyse_range(self, left_str: str, right_str: str, reverse: bool):
        self._range = True
        left_equal = False
        right_equal = False
        if left_str.endswith('='):
            left_str = left_str[:-1]
            left_equal = True
        try:
            if left_str:
                left_number = float(left_str)
            else:
                left_number = None
        except ValueError:
            raise ValueError(f'left half of {self._formula}:{left_str}is not a number')
        if right_str.startswith('='):
            right_str = right_str[1:]
            right_equal = True
        try:
            if right_str:
                right_number = float(right_str)
            else:
                right_number = None
        except ValueError:
            raise ValueError(f'right half of {self._formula}:{right_str}is not a number')
        if reverse:
            self._left = right_number
            self._left_equal = right_equal
            self._right = left_number
            self._right_equal = left_equal
        else:
            self._left = left_number
            self._left_equal = left_equal
            self._right = right_number
            self._right_equal = right_equal

    def check(self, check_number: Union[float, int]) -> bool:
        if self._range:
            left, right = True, True
            if self._left is not None:
                if self._left_equal:
                    left = check_number >= self._left
                else:
                    left = check_number > self._left
            if self._right is not None:
                if self._right_equal:
                    right = check_number <= self._right
                else:
                    right = check_number < self._right
            re_bool = left and right
        else:
            re_bool = check_number == self._middle
        if self._not:
            re_bool = not re_bool
        return re_bool


class CheckFormula:
    _OR = 'or'
    _AND = 'and'
    _NOT = 'not'
    _stop = ' '
    _operation = {
        '|': _OR,
        '&': _AND,
        '!': _NOT,
    }
    _left_child = '([{（【'
    _right_child = ')]}）】'
    _default_operation = _OR

    def __init__(self, formula: str, check_class=NumberCheck):
        self._str_formula = formula.strip(' ')
        self._check_class = check_class
        self._calculate_step = []
        self._list_formula = self._analyse_list(self._str_formula)
        self._now_formula = []
        self._result = None

    def __repr__(self):
        return f'CheckFormula({self._str_formula},{self._check_class.__name__})'

    @property
    def formula(self):
        return self._str_formula

    def _analyse_list(self, str_formula) -> list:
        re_list = []
        child = False
        bracket = 0
        now_str = ''
        for i, v in enumerate(str_formula):
            if child:
                now_str += v
                if v in self._right_child:
                    bracket -= 1
                    if bracket == 0:
                        re_list.append(self._analyse_list(now_str[:-1]))
                        child = False
                        now_str = ''
                elif v in self._left_child:
                    bracket += 1
            else:
                if v in self._left_child:
                    child = True
                    bracket = 1
                    if now_str:
                        re_list.append(self.one_formula_value(now_str))
                        now_str = ''
                elif v in self._right_child:
                    if now_str:
                        re_list.append(self.one_formula_value(now_str))
                        now_str = ''
                    re_list = [re_list]
                elif v in self._operation:
                    if now_str:
                        re_list.append(self.one_formula_value(now_str))
                        now_str = ''
                    re_list.append(self._operation[v])
                elif v in self._stop:
                    if now_str:
                        re_list.append(self.one_formula_value(now_str))
                        now_str = ''
                else:
                    now_str += v
        else:
            if now_str:
                re_list.append(self.one_formula_value(now_str))
        return self._fix_operation(re_list)

    def _fix_operation(self, list_formula):
        if len(list_formula) > 1:
            re_list = []
            for i, v in enumerate(list_formula[:-1]):
                re_list.append(v)
                w = list_formula[i + 1]
                if v not in self._operation.values() and w not in self._operation.values():
                    re_list.append(self._default_operation)
            re_list.append(list_formula[-1])
        else:
            re_list = [*list_formula]
        return re_list

    def one_formula_value(self, now_str):
        return self._check_class(now_str)

    def check(self, check_number: Union[float, int]) -> bool:
        if len(self._list_formula) > 0:
            self._now_formula = deepcopy(self._list_formula)
            self._calculate_step = []
            self._calculate_check(self._now_formula, check_number)
            self._record_one_step()
            self._result = self._calculate_loop_list(self._now_formula)
        else:
            self._result = True
        return self._result

    def _calculate_check(self, list_formula: list, check_number: Union[float, int]):
        for i, v in enumerate(list_formula):
            if isinstance(v, list):
                self._calculate_check(v, check_number)
            elif v not in self._operation.values() and hasattr(v, 'check'):
                list_formula[i] = v.check(check_number)

    def _calculate_loop_list(self, list_formula: list) -> bool:
        for i, v in enumerate(list_formula):
            if isinstance(v, list):
                start_step = len(self._calculate_step)
                list_formula[i] = self._calculate_loop_list(v)
                end_step = len(self._calculate_step)
                self._record_one_step(start_step != end_step)
        i = 0
        while i < len(list_formula) - 1:
            v = list_formula[i]
            if v == self._NOT:
                w = list_formula[i + 1]
                if isinstance(w, bool):
                    list_formula[i:i + 2] = [not w]
                    self._record_one_step()
                elif w == self._NOT:
                    list_formula[i:i + 2] = []
                    self._record_one_step()
                    i -= 1
                else:
                    raise ValueError(f'<not {w}> has no meaning.')
            i += 1
        i = 1
        while i < len(list_formula) - 1:
            v = list_formula[i]
            if v == self._AND:
                w1 = list_formula[i - 1]
                w2 = list_formula[i + 1]
                if isinstance(w1, bool) and isinstance(w2, bool):
                    list_formula[i - 1:i + 2] = [w1 and w2]
                    self._record_one_step()
                    i -= 2
                else:
                    raise ValueError(f'<{w1} and {w2}> has no meaning.')
            i += 1
        i = 1
        while i < len(list_formula) - 1:
            v = list_formula[i]
            if v == self._OR:
                w1 = list_formula[i - 1]
                w2 = list_formula[i + 1]
                if isinstance(w1, bool) and isinstance(w2, bool):
                    list_formula[i - 1:i + 2] = [w1 or w2]
                    self._record_one_step()
                    i -= 2
                else:
                    raise ValueError(f'<{w1} or {w2}> has no meaning.')
            i += 1
        if len(list_formula) == 1 and isinstance(list_formula[0], bool):
            return list_formula[0]
        else:
            raise ValueError(f'{list_formula} can not be calculate anymore')

    def show_all_step(self):
        re_str = self._str_formula + '\n' + str(self._list_formula)
        for i, v in enumerate(self._calculate_step):
            re_str += f'\n={v}'
        if self._result is not None:
            re_str += f'\n={self._result}'
        return re_str

    def _record_one_step(self, replace=False):
        if replace:
            self._calculate_step[-1] = deepcopy(self._now_formula)
        else:
            self._calculate_step.append(deepcopy(self._now_formula))
