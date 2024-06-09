#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : decorator
# Author        : Sun YiFan-Movoid
# Time          : 2024/1/28 16:05
# Description   : 
"""
import inspect
from inspect import Parameter, Signature
from types import CodeType, FunctionType
from typing import Union, Dict, List


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


def analyse_args_value_from_function(func, *args, **kwargs):
    re_dict = {
        'arg': {},
        'kwarg': {},
    }
    arg_dict = get_args_dict_from_function(func)
    for i, v in enumerate(arg_dict['arg'].keys()):
        re_dict['arg'][v] = args[i]
    if arg_dict['args']:
        re_dict['args'] = {}
        v = list(arg_dict['args'].keys())[0]
        re_dict['args'][f'{v}'] = list(args[len(arg_dict['arg']):])
    for i in arg_dict['kwarg']:
        re_dict['kwarg'][i] = kwargs[i]
    if arg_dict['kwargs']:
        key = list(arg_dict['kwargs'].keys())[0]
        re_dict['kwargs'] = {key: {}}
        temp_kw = {}
        for i, v in kwargs.items():
            if i not in arg_dict['kwarg']:
                temp_kw[i] = v
        re_dict['kwargs'][key] = temp_kw
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


def recover_signature_from_function_func(ori_func, *args):
    def dec(run_func):
        def wrapper():
            __local = locals()
            __func_kwargs = {}
            for __i, __v in func_arg.items():  # noqa
                if __i == '':
                    for __v2 in __v:
                        __func_kwargs[__v2] = __local[__v2]
                else:
                    __func_kwargs[__i] = {}
                    for __v2 in __v:
                        __func_kwargs[__i][__v2] = __local[__v2]
            return func(**__func_kwargs)  # noqa

        func_arg_dict = {
            '': []
        }
        parameter_dict = {
            'arg': {},
            'arg_default': {},
            'kwarg': {},
        }
        parameters = []
        docs = [ori_func.__doc__, run_func.__doc__]
        annotations = {}

        run_kw_parameter = [i for i, v in Signature.from_callable(run_func).parameters.items() if v.default == Parameter.empty and 'kw' in i]
        for i, v in Signature.from_callable(run_func).parameters.items():
            if i not in run_kw_parameter:
                func_arg_dict[''].append(i)
                if v.default == Parameter.empty:
                    parameter_dict['arg'].setdefault(i, v)
                else:
                    parameter_dict['kwarg'].setdefault(i, Parameter(i, Parameter.KEYWORD_ONLY, default=v.default, annotation=v.annotation))

        if len(run_kw_parameter) == len(args):
            args_kw_parameter = run_kw_parameter
        elif len(run_kw_parameter) == len(args) + 1:
            args_kw_parameter = run_kw_parameter[1:]
            kwargs_name = run_kw_parameter[0]
            func_arg_dict[kwargs_name] = []
            for i, v in Signature.from_callable(ori_func).parameters.items():
                func_arg_dict[kwargs_name].append(i)
                if v.kind == Parameter.POSITIONAL_OR_KEYWORD:
                    if v.default is Parameter.empty:
                        parameter_dict['arg'].setdefault(i, v)
                    else:
                        parameter_dict['arg_default'].setdefault(i, v)
                elif v.kind == Parameter.KEYWORD_ONLY:
                    parameter_dict['kwarg'].setdefault(i, v)
        else:
            raise TypeError(f'you should set {len(args)}~{len(args) + 1} positional arguments contains words "kw" in wrapper function for {args},but you set {len(run_kw_parameter)} only')

        for func_index, function in enumerate(args):
            kwargs_name = args_kw_parameter[func_index]
            func_arg_dict[kwargs_name] = []
            docs.append(function.__doc__)
            annotations.update(function.__annotations__)
            for i, v in Signature.from_callable(function).parameters.items():
                func_arg_dict[kwargs_name].append(i)
                if v.kind == Parameter.POSITIONAL_OR_KEYWORD:
                    if v.default is Parameter.empty:
                        parameter_dict['arg'].setdefault(i, v)
                    else:
                        parameter_dict['arg_default'].setdefault(i, v)
                elif v.kind == Parameter.KEYWORD_ONLY:
                    parameter_dict['kwarg'].setdefault(i, v)

        for i, v in parameter_dict['arg'].items():
            parameters.append(v)
        for i, v in parameter_dict['arg_default'].items():
            parameters.append(v)
        for i, v in parameter_dict['kwarg'].items():
            parameters.append(v)
        annotations.update(run_func.__annotations__)
        wrap_code = wrapper.__code__
        ori_code: CodeType = ori_func.__code__
        mod_co_arg_count = len([_v for _v in parameters if _v.kind == Parameter.POSITIONAL_OR_KEYWORD])
        mod_co_kwarg_count = len([_v for _v in parameters if _v.kind == Parameter.KEYWORD_ONLY])
        mod_co_n_locals = len(parameters) + wrap_code.co_nlocals
        mod_co_flags = wrap_code.co_flags
        var_names = [_v.name for _v in parameters]
        mod_co_flags = mod_co_flags | inspect.CO_VARARGS - inspect.CO_VARARGS
        mod_co_flags = mod_co_flags | inspect.CO_VARKEYWORDS - inspect.CO_VARKEYWORDS
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

        modified_func = FunctionType(final_code, {'func': run_func, 'func_arg': func_arg_dict, 'locals': locals}, name=mod_co_name)
        modified_func.__doc__ = '\n'.join([_ for _ in docs if _])
        modified_func.__annotations__ = annotations
        modified_func.__defaults__ = default_arg_values
        modified_func.__kwdefaults__ = default_kwarg_values
        return modified_func

    return dec


def reset_function_default_value(ori_func):
    def dec(run_func):
        @recover_signature_from_function_func(run_func, ori_func)
        def wrapper(ori_kwargs):
            return ori_func(**ori_kwargs)

        run_parameter = {i: v for i, v in Signature.from_callable(run_func).parameters.items()}
        default_arg_values = []
        default_kwarg_values = {}
        for i, v in Signature.from_callable(ori_func).parameters.items():
            if v.default != Parameter.empty:
                if v.kind == Parameter.POSITIONAL_OR_KEYWORD:
                    if i in run_parameter and run_parameter[i].default != Parameter.empty:
                        default_arg_values.append(run_parameter[i].default)
                    else:
                        default_arg_values.append(v.default)
                elif v.kind == Parameter.KEYWORD_ONLY:
                    if i in run_parameter and run_parameter[i].default != Parameter.empty:
                        default_kwarg_values[i] = run_parameter[i].default
                    else:
                        default_kwarg_values[i] = v.default

        wrapper.__defaults__ = tuple(default_arg_values)
        wrapper.__kwdefaults__ = default_kwarg_values
        return wrapper

    return dec
