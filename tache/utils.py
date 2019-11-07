#!/usr/bin/env python
# -*- coding: utf-8 -*-
import six

from .shortid import short_id


def key_for_fn(namespace, fn):
    classname = None
    if six.PY2:
        if hasattr(fn, 'im_class'):
            classname = fn.im_class.__name__
            if classname == 'type':
                classname = fn.im_self.__name__
    else:
        if hasattr(fn, '__self__'):
            classname = fn.__self__.__class__.__name__
            if classname == 'type':
                classname = fn.__self__.__name__
    if classname:
        key = "{0}.{1}.{2}".format(fn.__module__, classname, fn.__name__)
    else:
        key = "{0}.{1}".format(fn.__module__, fn.__name__)
    if namespace is None:
        return key
    else:
        return '{0}:{1}'.format(namespace, key)


def arguments_key_generator(namespace, fn, *args, **kwargs):
    key = key_for_fn(namespace, fn)
    if kwargs:
        raise ValueError(
            "tcache's default key_func"
            "function does not accept keyword arguments.")
    args = [six.ensure_str(arg) if isinstance(arg, six.string_types) else arg for arg in args ]
    return key + "|" + "-".join(map(str, args))


def kwargs_key_generator(namespace, fn, *args, **kwargs):
    key = key_for_fn(namespace, fn)
    if args:
        raise ValueError(
            "kwargs key generator does not accept positional arguments")

    return key + "|" + ','.join(map(str, sorted(kwargs.items(), key=lambda x: x[0])))


def arguments_batch_keys_generator(namespace, fn, *args):
    key = key_for_fn(namespace, fn)
    return [key + "|" + k for k in map(str, args)]


def tag_key_generator(backend, prefix, tag_prefix, tags, timeout, *args, **kwargs):
    src_keys = []
    for t in tags:
        if callable(t):
            tag = str(t(*args, **kwargs))
        else:
            tag = str(t.format(*args, **kwargs))
        key = tag_prefix + tag
        src_keys.append(key)
    dst_keys = backend.mget(src_keys)
    for idx, dst_key in enumerate(dst_keys):
        if dst_key is NO_VALUE:
            src_key = src_keys[idx]
            tag_key = short_id()
            backend.set(src_key, tag_key, timeout)
            dst_keys[idx] = tag_key
    return prefix + "|" + "-".join(map(str, dst_keys))


class NoValue(object):
    """Describe a missing cache value.

    The :attr:`.NO_VALUE` module global
    should be used.
    """
    __slots__ = tuple()

    def __repr__(self):
        return 'NoValue'


NO_VALUE = NoValue()
