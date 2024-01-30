#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : decorator
# Author        : Sun YiFan-Movoid
# Time          : 2024/1/28 16:05
# Description   : 
"""
import inspect
from types import CodeType, FunctionType
from typing import Union, Dict, List
from inspect import Parameter, Signature


def get_args_dict_from_function(func) -> Dict[str, Dict[str, Parameter]]:
    re_dict = {
        'arg': {},
        'args': {},
        'kwarg': {},
        'kwargs': {}
    }
    for i, v in Signature.from_callable(func).parameters.items():
        if v.kind == Parameter.VAR_KEYWORD:
            re_dict['kwargs'][i] = v
        elif v.kind == Parameter.VAR_POSITIONAL:
            re_dict['args'][i] = v
        elif v.kind == Parameter.KEYWORD_ONLY:
            re_dict['kwarg'][i] = v
        else:
            re_dict['arg'][i] = v
    return re_dict


def combine_parameter_from_functions(ori_func, run_func) -> List[Parameter]:
    re_list = []
    ori_dict = get_args_dict_from_function(ori_func)
    run_dict = get_args_dict_from_function(run_func)
    for i, v in run_dict['arg'].items():
        if i not in ori_dict['arg']:
            re_list.append(v)
    for i, v in ori_dict['arg'].items():
        re_list.append(v)
    for i, v in ori_dict['args'].items():
        re_list.append(v)
    for i, v in ori_dict['kwarg'].items():
        re_list.append(v)
    for i, v in run_dict['kwarg'].items():
        if i not in ori_dict['kwarg']:
            re_list.append(v)
    for i, v in ori_dict['kwargs'].items():
        re_list.append(v)
    return re_list


def get_args_name_from_parameters(parameters: List[Parameter]) -> Dict[str, Union[str, List[str]]]:
    re_dict = {
        'arg': [],
        'args': '',
        'kwarg': [],
        'kwargs': ''
    }
    for v in parameters:
        if v.kind == Parameter.VAR_KEYWORD:
            re_dict['kwargs'] = v.name
        elif v.kind == Parameter.VAR_POSITIONAL:
            re_dict['args'] = v.name
        elif v.kind == Parameter.KEYWORD_ONLY:
            re_dict['kwarg'].append(v.name)
        else:
            re_dict['arg'].append(v.name)

    return re_dict


def recover_signature_from_function(ori_func):
    def dec(run_func):
        def wrapper():
            __local = locals()
            __func_args = []
            __func_kwargs = {}
            for __i in func_arg['arg']:  # noqa
                if __i in __local:
                    __func_args += [__local[__i]]
            if func_arg['args'] and func_arg['args'] in __local:  # noqa
                __func_args += __local[func_arg['args']]  # noqa
            for __i in func_arg['kwarg']:  # noqa
                __func_kwargs[__i] = __local[__i]  # noqa
            if func_arg['kwargs'] and func_arg['kwargs'] in __local:  # noqa
                __func_kwargs.update(__local[func_arg['kwargs']])  # noqa
            return func(*__func_args, **__func_kwargs)  # noqa

        parameters = combine_parameter_from_functions(ori_func, run_func)
        func_arg_list = get_args_name_from_parameters(parameters)
        wrap_code = wrapper.__code__
        ori_code: CodeType = ori_func.__code__

        mod_co_arg_count = len([_v for _v in parameters if _v.kind == Parameter.POSITIONAL_OR_KEYWORD])
        mod_co_kwarg_count = len([_v for _v in parameters if _v.kind == Parameter.KEYWORD_ONLY])
        mod_co_n_locals = len(parameters) + wrap_code.co_nlocals
        mod_co_flags = wrap_code.co_flags
        var_names = []
        var_names_arg = None
        var_names_kwarg = None
        for _v in parameters:
            if _v.kind == Parameter.VAR_POSITIONAL:
                var_names_arg = _v.name
            elif _v.kind == Parameter.VAR_KEYWORD:
                var_names_kwarg = _v.name
            else:
                var_names.append(_v.name)
        if var_names_arg is not None:
            var_names.append(var_names_arg)
            mod_co_flags = mod_co_flags | inspect.CO_VARARGS
        if var_names_kwarg is not None:
            var_names.append(var_names_kwarg)
            mod_co_flags = mod_co_flags | inspect.CO_VARKEYWORDS
        mod_co_var_names = tuple(var_names)
        mod_co_name = ori_code.co_name
        default_arg_values = []
        default_kwarg_values = {}
        for _v in parameters:
            if _v.default != Parameter.empty:
                if _v.kind == Parameter.POSITIONAL_OR_KEYWORD:
                    default_arg_values.append(_v.default)
                elif _v.kind == Parameter.KEYWORD_ONLY:
                    default_kwarg_values[_v.name] = _v.default
        default_arg_values = tuple(default_arg_values)

        final_code = wrap_code.replace(
            co_argcount=mod_co_arg_count,
            co_kwonlyargcount=mod_co_kwarg_count,
            co_nlocals=mod_co_n_locals,
            co_varnames=mod_co_var_names,
            co_name=mod_co_name,
            co_flags=mod_co_flags,
        )

        modified_func = FunctionType(final_code, {'func': run_func, 'func_arg': func_arg_list, 'locals': locals}, name=mod_co_name)
        ori_doc = '' if ori_func.__doc__ is None else ori_func.__doc__
        run_doc = '' if run_func.__doc__ is None else run_func.__doc__
        modified_func.__doc__ = ori_doc + '\n' + run_doc
        modified_func.__doc__.strip('\n')
        modified_func.__annotations__ = ori_func.__annotations__
        modified_func.__defaults__ = default_arg_values
        modified_func.__kwdefaults__ = default_kwarg_values
        return modified_func

    return dec


def recover_signature_from_function_only_kwargs(ori_func):
    def dec(run_func):
        def wrapper():
            __local = locals()
            __func_kwargs = {}
            for __i in func_arg['arg']:  # noqa
                if __i in __local:
                    __func_kwargs[__i] = [__local[__i]]
            if func_arg['args'] and func_arg['args'] in __local:  # noqa
                __func_kwargs[func_arg['args']] = __local[func_arg['args']]  # noqa
            for __i in func_arg['kwarg']:  # noqa
                __func_kwargs[__i] = __local[__i]  # noqa
            if func_arg['kwargs'] and func_arg['kwargs'] in __local:  # noqa
                __func_kwargs.update(__local[func_arg['kwargs']])  # noqa
            return func(**__func_kwargs)  # noqa

        parameters = combine_parameter_from_functions(ori_func, run_func)
        func_arg_list = get_args_name_from_parameters(parameters)
        wrap_code = wrapper.__code__
        ori_code: CodeType = ori_func.__code__

        mod_co_arg_count = len([_v for _v in parameters if _v.kind == Parameter.POSITIONAL_OR_KEYWORD])
        mod_co_kwarg_count = len([_v for _v in parameters if _v.kind == Parameter.KEYWORD_ONLY])
        mod_co_n_locals = len(parameters) + wrap_code.co_nlocals
        mod_co_flags = wrap_code.co_flags
        var_names = []
        var_names_arg = None
        var_names_kwarg = None
        for _v in parameters:
            if _v.kind == Parameter.VAR_POSITIONAL:
                var_names_arg = _v.name
            elif _v.kind == Parameter.VAR_KEYWORD:
                var_names_kwarg = _v.name
            else:
                var_names.append(_v.name)
        if var_names_arg is not None:
            var_names.append(var_names_arg)
            mod_co_flags = mod_co_flags | inspect.CO_VARARGS
        if var_names_kwarg is not None:
            var_names.append(var_names_kwarg)
            mod_co_flags = mod_co_flags | inspect.CO_VARKEYWORDS
        mod_co_var_names = tuple(var_names)
        mod_co_name = ori_code.co_name
        default_arg_values = []
        default_kwarg_values = {}
        for _v in parameters:
            if _v.default != Parameter.empty:
                if _v.kind == Parameter.POSITIONAL_OR_KEYWORD:
                    default_arg_values.append(_v.default)
                elif _v.kind == Parameter.KEYWORD_ONLY:
                    default_kwarg_values[_v.name] = _v.default
        default_arg_values = tuple(default_arg_values)

        final_code = wrap_code.replace(
            co_argcount=mod_co_arg_count,
            co_kwonlyargcount=mod_co_kwarg_count,
            co_nlocals=mod_co_n_locals,
            co_varnames=mod_co_var_names,
            co_name=mod_co_name,
            co_flags=mod_co_flags,
        )

        modified_func = FunctionType(final_code, {'func': run_func, 'func_arg': func_arg_list, 'locals': locals}, name=mod_co_name)
        ori_doc = '' if ori_func.__doc__ is None else ori_func.__doc__
        run_doc = '' if run_func.__doc__ is None else run_func.__doc__
        modified_func.__doc__ = ori_doc + '\n' + run_doc
        modified_func.__doc__.strip('\n')
        modified_func.__annotations__ = ori_func.__annotations__
        modified_func.__defaults__ = default_arg_values
        modified_func.__kwdefaults__ = default_kwarg_values
        return modified_func

    return dec
