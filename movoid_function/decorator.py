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
    """
    获得函数的参数分类，一共分成四类，返回一个4键值的dict
    :param func: 目标函数
    :return: key分别是arg、args、kwarg、kwargs的dict
    """
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
    """
    获得函数和对其传入的参数，解析每个参数分别的类型，和名称-值的对应关系
    :param func: 目标函数
    :param args: 参数，原样传入
    :param kwargs: 参数，原样传入
    :return: 一个dict，包含2~4个key：arg[、args]、kwarg[、kwargs]
    """
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
    """
    获得两个函数，返回两个函数的合成函数的参数列表
    :param ori_func: 原始函数（被装饰器传入的）
    :param run_func: 运行函数（被装饰器装饰的）
    :return: 合成的参数列表
    """
    re_list = []
    ori_dict = get_args_dict_from_function(ori_func)
    run_dict = get_args_dict_from_function(run_func)
    for i, v in ori_dict['arg'].items():
        if v.default == Parameter.empty:
            re_list.append(v)
    for i, v in run_dict['arg'].items():
        if i not in ori_dict['arg'] and v.default == Parameter.empty:
            re_list.append(v)
    for i, v in ori_dict['arg'].items():
        if v.default != Parameter.empty:
            re_list.append(v)
    for i, v in run_dict['arg'].items():
        if i not in ori_dict['arg'] and v.default != Parameter.empty:
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
    """
    从一个parameter的列表中获取所有的arg名称，并且转换为一组dict，可以很有效地明确具体哪个参数是什么kind
    :param parameters: 参数列表
    :return: 合成的dict
    """
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


def analyse_additional_parameter(name, default=Parameter.empty, kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=None):
    """
    将一组信息转换为parameter，参数和Parameter的参数完全一致，只是增加了默认值
    :param name:
    :param default:
    :param kind:
    :param annotation:
    :return:
    """
    if isinstance(name, list):
        new_parameter = analyse_additional_parameter(*name)
    elif isinstance(name, dict):
        new_parameter = Parameter(**name)
    else:
        new_parameter = Parameter(name=str(name), kind=kind, default=default, annotation=annotation)
    return new_parameter


def insert_parameter_into_parameters(parameters: list, *new_parameters):
    """
    将新的参数插入到已有的参数列表中，保证其不混乱
    :param parameters: 已有的参数列表
    :param new_parameters: 新的参数，以*args的方式传入即可
    :return: 无，传入的list已经被改变了
    """
    if len(new_parameters) == 0:
        return
    if len(parameters) == 0:
        parameters.append(new_parameters[0])
        insert_parameter_into_parameters(parameters, *new_parameters[1:])
    i = 0
    last_priority = 0
    new_parameter_priority = [get_parameter_priority(_) for _ in new_parameters]
    while i < len(parameters):
        v = parameters[i]
        v_priority = get_parameter_priority(v)
        if v_priority != last_priority and v_priority > 1:
            for j, w in enumerate(new_parameter_priority):
                if w < v_priority:
                    parameters.insert(i, new_parameters[j])
                    i += 1
        i += 1


def get_parameter_priority(parameter):
    """
    获取parameter地优先级，一般来说是：positional无默认、positional有默认、*args、keyword、**kwargs
    :param parameter:
    :return:
    """
    if parameter.kind == Parameter.POSITIONAL_ONLY:
        return 1
    if parameter.kind == Parameter.POSITIONAL_OR_KEYWORD:
        if parameter.default == Parameter.empty:
            return 2
        else:
            return 3
    elif parameter.kind == Parameter.VAR_POSITIONAL:
        return 5
    elif parameter.kind == Parameter.KEYWORD_ONLY:
        return 6
    elif parameter.kind == Parameter.VAR_KEYWORD:
        return 10


def create_function_with_parameters_function_args(
        parameters,
        real_run_func,
        run_arg_list: dict,
        wrapper,
        func_name: str,
        func_doc: str
):
    """
    可以按照既定的参数生成一个函数
    :param parameters: 新函数的parameters
    :param real_run_func: 实际要被运行的函数
    :param run_arg_list: 实际要被运行的函数的参数列表
    :param wrapper: wrapper函数
    :param func_name: 新函数名称，一般为ori_func的名称
    :param func_doc: 新函数的注释，一般为函数的合并
    :return: 返回目标函数
    """
    wrap_code = wrapper.__code__

    mod_co_arg_count = len([_v for _v in parameters if _v.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)])
    mod_co_kwarg_count = len([_v for _v in parameters if _v.kind == Parameter.KEYWORD_ONLY])
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
    for _var_name in wrap_code.co_varnames:
        if _var_name not in var_names:
            var_names.append(_var_name)
    mod_co_var_names = tuple(var_names)
    mod_co_name = func_name
    default_arg_values = []
    default_kwarg_values = {}
    for _v in parameters:
        if _v.default != Parameter.empty:
            if _v.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
                default_arg_values.append(_v.default)
            elif _v.kind == Parameter.KEYWORD_ONLY:
                default_kwarg_values[_v.name] = _v.default
    default_arg_values = tuple(default_arg_values)

    final_code = wrap_code.replace(
        co_argcount=mod_co_arg_count,
        co_kwonlyargcount=mod_co_kwarg_count,
        co_nlocals=len(mod_co_var_names),
        co_varnames=mod_co_var_names,
        co_name=mod_co_name,
        co_flags=mod_co_flags,
    )
    func_annotations = {_.name: _.annotation for _ in parameters if _.annotation != Parameter.empty}

    modified_func = FunctionType(final_code, {'func': real_run_func, 'func_arg': run_arg_list, 'locals': locals}, name=mod_co_name)
    modified_func.__doc__ = func_doc
    modified_func.__annotations__ = func_annotations
    modified_func.__defaults__ = default_arg_values
    modified_func.__kwdefaults__ = default_kwarg_values
    return modified_func


def wraps(ori_func):
    """
    装饰器专用，保证被装饰器装饰后的函数，保证名称、参数列表等信息不会因为装饰和发生巨大异变，是一个比function tool的wraps更好的装饰器专用装饰器
    :param ori_func:
    :return:
    """

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
        ori_code: CodeType = ori_func.__code__
        annotations = {}
        annotations.update(run_func.__annotations__)
        annotations.update(ori_func.__annotations__)

        ori_doc = '' if ori_func.__doc__ is None else ori_func.__doc__
        run_doc = '' if run_func.__doc__ is None else run_func.__doc__
        all_doc = ori_doc + '\n' + run_doc
        all_doc.strip('\n')
        if all_doc == '':
            all_doc = None

        return create_function_with_parameters_function_args(
            parameters=parameters,
            real_run_func=run_func,
            run_arg_list=func_arg_list,
            wrapper=wrapper,
            func_name=ori_code.co_name,
            func_doc=all_doc
        )

    return dec


def wraps_kw(ori_func):
    """
    装饰器专用装饰器，可以在没有*args的情况下，把所有参数都通过kwargs的形式传入
    :param ori_func:
    :return:
    """

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
        ori_code: CodeType = ori_func.__code__
        annotations = {}
        annotations.update(run_func.__annotations__)
        annotations.update(ori_func.__annotations__)

        ori_doc = '' if ori_func.__doc__ is None else ori_func.__doc__
        run_doc = '' if run_func.__doc__ is None else run_func.__doc__
        all_doc = ori_doc + '\n' + run_doc
        all_doc.strip('\n')
        if all_doc == '':
            all_doc = None

        return create_function_with_parameters_function_args(
            parameters=parameters,
            real_run_func=run_func,
            run_arg_list=func_arg_list,
            wrapper=wrapper,
            func_name=ori_code.co_name,
            func_doc=all_doc
        )

    return dec


def wraps_func(ori_func, *args):
    """
    装饰器专用装饰器
    传入若干个函数，可以令被装饰器装饰的函数执行若干个函数的功能，但是必须保证这些函数在传入的时候没有*args，以保证每个函数都能精准传递参数
    :param ori_func: 一般是被装饰器装饰的函数，
    :param args: 每个都必须是一个函数
    :return:
    """

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
                if v.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
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
                if v.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
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
        mod_co_arg_count = len([_v for _v in parameters if _v.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)])
        mod_co_kwarg_count = len([_v for _v in parameters if _v.kind == Parameter.KEYWORD_ONLY])
        mod_co_flags = wrap_code.co_flags
        var_names = [_v.name for _v in parameters]
        mod_co_flags = mod_co_flags | inspect.CO_VARARGS - inspect.CO_VARARGS
        mod_co_flags = mod_co_flags | inspect.CO_VARKEYWORDS - inspect.CO_VARKEYWORDS
        for _var_name in wrap_code.co_varnames:
            if _var_name not in var_names:
                var_names.append(_var_name)
        mod_co_var_names = tuple(var_names)
        mod_co_name = ori_code.co_name
        default_arg_values = []
        default_kwarg_values = {}
        for _v in parameters:
            if _v.default != Parameter.empty:
                if _v.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
                    default_arg_values.append(_v.default)
                elif _v.kind == Parameter.KEYWORD_ONLY:
                    default_kwarg_values[_v.name] = _v.default
        default_arg_values = tuple(default_arg_values)

        final_code = wrap_code.replace(
            co_argcount=mod_co_arg_count,
            co_kwonlyargcount=mod_co_kwarg_count,
            co_nlocals=len(mod_co_var_names),
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
    """
    如果想要定义一个函数，这个函数的功能和已有的函数完全一致，但是默认输入值发生变化，那么可以用这个来作为装饰器
    被装饰的函数内部不需要有任何执行内容，输入pass即可（输入任何内容都不会执行）
    根据被装饰的函数的参数输入的默认值来作为新的默认值。没有输入的话，则使用原函数的默认值
    样例如下：
def test1(a=1,b=2,c=4):
    ...

@reset_function_default_value
def test2(a=2):
    pass

    此时test2就是一个默认值为a=2,b=2,c=4的执行test1完整功能的函数
    这个功能可以有效地创建一些傻瓜函数
    :param ori_func: 目标函数，也就是需要被copy的函数
    """

    def dec(run_func):
        @wraps_func(run_func, ori_func)
        def wrapper(ori_kwargs):
            return ori_func(**ori_kwargs)

        run_parameter = {i: v for i, v in Signature.from_callable(run_func).parameters.items()}
        default_arg_values = []
        default_kwarg_values = {}
        for i, v in Signature.from_callable(ori_func).parameters.items():
            if v.default != Parameter.empty:
                if v.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
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


def wraps_ori(ori_func):
    """
    装饰器专用函数，本身执行的时候只运行ori函数本身，完全忽略run func。只是允许run func额外传入一些参数而已
    :param ori_func:
    """

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
        func_arg_list = get_args_name_from_parameters(list(Signature.from_callable(ori_func).parameters.values()))
        ori_code: CodeType = ori_func.__code__

        return create_function_with_parameters_function_args(
            parameters=parameters,
            real_run_func=ori_func,
            run_arg_list=func_arg_list,
            wrapper=wrapper,
            func_name=ori_code.co_name,
            func_doc=ori_func.__doc__
        )

    return dec


def wraps_add_one(name, default=Parameter.empty, kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=None):
    """
    装饰器专用函数，对函数新增一个参数
    :param name: 参数名
    :param default: 参数默认值，默认没有
    :param kind: 参数类型，默认POSITIONAL_OR_KEYWORD
    :param annotation: 参数的注释，默认为空
    """

    def dec(ori_func):
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

        parameters = list(Signature.from_callable(ori_func).parameters.values())
        new_parameter = analyse_additional_parameter(name=name, default=default, kind=kind, annotation=annotation)
        insert_parameter_into_parameters(parameters, new_parameter)
        func_arg_list = get_args_name_from_parameters(parameters)
        ori_code: CodeType = ori_func.__code__

        return create_function_with_parameters_function_args(
            parameters=parameters,
            real_run_func=ori_func,
            run_arg_list=func_arg_list,
            wrapper=wrapper,
            func_name=ori_code.co_name,
            func_doc=ori_func.__doc__
        )

    return dec


def wraps_add_multi(*parameters_info):
    """
    装饰器专用函数，对函数新增不定多个参数
    :param parameters_info: 每个参数都必须是一个列表，列表长度为1~4，分别对应name（名称）、default（默认值，默认没有默认值）、kind（参数类型，默认POSITIONAL_OR_KEYWORD）、annotation（注释，默认为空）
    """

    def dec(ori_func):
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

        parameters = list(Signature.from_callable(ori_func).parameters.values())
        new_parameters = [analyse_additional_parameter(_) for _ in parameters_info]
        insert_parameter_into_parameters(parameters, *new_parameters)
        func_arg_list = get_args_name_from_parameters(list(Signature.from_callable(ori_func).parameters.values()))
        ori_code: CodeType = ori_func.__code__

        return create_function_with_parameters_function_args(
            parameters=parameters,
            real_run_func=ori_func,
            run_arg_list=func_arg_list,
            wrapper=wrapper,
            func_name=ori_code.co_name,
            func_doc=ori_func.__doc__,
        )

    return dec


def adapt_call(ori_func, ori_args=None, ori_kwargs=None, other_func=None, other_args=None, other_kwargs=None, force=False):
    """
    在基础args和kwargs上，使用其他的args和kwargs对初始args和kwargs进行补充。在补充完毕后，传入函数进行运行。
    如果基础的args和kwargs存在多余的参数，那么也会被相应的删除
    :param ori_func: 原始的function
    :param ori_args: 基础args
    :param ori_kwargs: 基础kwargs
    :param other_func: 其他来源的function
    :param other_args: 补充args
    :param other_kwargs: 补充kwargs
    :param force: 即使存在默认值，也会从other参数中选择并填充
    :return: 运行完毕后，返回
    """
    args = []
    kwargs = {}
    arg_dict = {}
    ori_args = [] if ori_args is None else list(ori_args)
    ori_kwargs = {} if ori_kwargs is None else dict(ori_kwargs)
    other_dict = {}
    if other_func is not None:
        other_args = [] if other_args is None else list(other_args)
        other_kwargs = {} if other_kwargs is None else dict(other_kwargs)
        other_arg_dict = analyse_args_value_from_function(other_func, *other_args, **other_kwargs)
        for key in ['arg', 'args', 'kwarg']:
            other_dict.update(other_arg_dict.get(key, {}))
        if other_arg_dict.get('kwargs'):
            other_dict.update(list(other_arg_dict['kwargs'].values())[0])
    ori_arg_dict = get_args_dict_from_function(ori_func)
    now_index = 0
    used_kwarg_key = []
    for name, parameter in ori_arg_dict['arg'].items():
        if len(ori_args) > now_index:
            args.append(ori_args[now_index])
        elif name in ori_kwargs:
            args.append(ori_kwargs[name])
            used_kwarg_key.append(name)
        elif force or parameter.default is Signature.empty:
            if name in other_dict:
                args.append(other_dict[name])
        else:
            args.append(parameter.default)
        now_index += 1
    if ori_arg_dict['args']:
        args += ori_args[now_index:]
    for name, parameter in ori_arg_dict['kwarg'].items():
        if name in used_kwarg_key:
            continue
        elif name in ori_kwargs:
            kwargs[name] = ori_kwargs[name]
            used_kwarg_key.append(name)
        elif force or parameter.default is Signature.empty:
            if name in other_dict:
                kwargs[name] = other_dict[name]
        else:
            kwargs[name] = parameter.default
    if ori_arg_dict['kwargs']:
        for key, value in ori_kwargs.items():
            if key not in used_kwarg_key:
                kwargs[key] = value
    return ori_func(*args, **kwargs)
