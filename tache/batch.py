#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量缓存接口
"""
import functools
import types

from .utils import NO_VALUE


class Batch(object):

    def __init__(self, func, backend, keys_func, timeout,
                 namespace):
        self._func = func
        self._backend = backend
        self._keys_func = keys_func
        self._timeout = timeout
        self._namespace = namespace
        if isinstance(self._func, (classmethod, staticmethod)):
            functools.update_wrapper(self, self._func.__func__)
        else:
            functools.update_wrapper(self, self._func)

    def __get__(self, instance, owner):
        wrapped_self = object.__new__(self.__class__)
        wrapped_self.__dict__ = self.__dict__.copy()
        if instance is None:
            if not hasattr(self._func, "__call__"):
                wrapped_self._func = self._func.__get__(None, owner)
            return wrapped_self
        if not isinstance(self._func, types.MethodType):
            wrapped_self._func = self._func.__get__(instance, owner)
        return wrapped_self

    def __call__(self, *args, **kwargs):
        if kwargs:
            raise ValueError("batch decorators only support positional arguments")
        if not args:
            return []
        cache_keys = self._keys_func(self._namespace, self._func, *args)
        key_lookup = dict(zip(args, cache_keys))
        mapping = dict(zip(args, self._backend.mget(cache_keys)))
        miss_args = []
        for arg, value in mapping.items():
            if value is NO_VALUE:
                miss_args.append(arg)
        if miss_args:
            miss_mapping = dict(zip(miss_args, self._func(*[arg for arg in miss_args])))
            miss_cache_mapping = dict((key_lookup[arg], v) for (arg, v) in miss_mapping.items())
            self._backend.mset(miss_cache_mapping, self._timeout)
            mapping.update(miss_mapping)
        return [mapping[arg] for arg in args]

    def invalidate(self, *args):
        cache_keys = self._keys_func(self._namespace, self._func, *args)
        self._backend.delete(*cache_keys)
