#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import types

from .utils import tag_key_generator, NO_VALUE


class Cached(object):

    def __init__(self, func, backend, key_func, timeout,
                 namespace, tags, should_cache_fn, tag_prefix):
        self._func = func
        self._backend = backend
        self._key_func = key_func
        self._timeout = timeout
        self._tags = tags
        self._namespace = namespace
        self._should_cache_fn = should_cache_fn
        self._tag_prefix = tag_prefix
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
        cache_key = self._key_func(self._namespace, self._func, *args, **kwargs)
        if self._tags:
            cache_key = tag_key_generator(self._backend, cache_key, self._tag_prefix,
                                          self._tags, self._timeout, *args, **kwargs)
        result = self._backend.get(cache_key)
        if result is NO_VALUE:
            result = self._func(*args, **kwargs)
            if self._should_cache_fn(result):
                self._backend.set(cache_key, result, self._timeout)
        return result

    def invalidate(self, *args, **kwargs):
        cache_key = self._key_func(self._namespace, self._func, *args, **kwargs)
        if self._tags:
            cache_key = tag_key_generator(self._backend, cache_key, self._tag_prefix,
                                          self._tags, self._timeout, *args, **kwargs)
        self._backend.delete(cache_key)

    def invalidate_tag(self, tag):
        key = self._tag_prefix + tag
        self._backend.delete(key)

    def nocache(self, *args, **kwargs):
        """
        directly call, without cache
        """
        return self._func(*args, **kwargs)

    def refresh(self, *args, **kwargs):
        cache_key = self._key_func(self._namespace, self._func, *args, **kwargs)
        result = self._func(*args, **kwargs)
        if self._should_cache_fn(result):
            self._backend.set(cache_key, result, self._timeout)
        return result
