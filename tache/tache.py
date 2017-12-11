#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tache
"""
from .batch import Batch
from .cached import Cached
from .utils import (arguments_key_generator,
                    arguments_batch_keys_generator,
                    )
from ._compat import basestring


class Tache(object):
    def __init__(self, backend_cls, default_key_generator=arguments_key_generator, tag_prefix="tag:", **kwargs):
        self.backend = backend_cls(**kwargs)
        self.default_key_generator = default_key_generator
        self.tag_prefix = tag_prefix

    def cached(self, key_func=None, timeout=3600, namespace=None, tags=None,
               should_cache_fn=lambda _: True):
        origin_key_func = key_func
        if isinstance(origin_key_func, basestring):
            key_func = lambda namespace, fn, *args, **kwargs: origin_key_func.format(*args, **kwargs) # noqa
        else:
            key_func = key_func or self.default_key_generator
        return lambda fn: Cached(fn, backend=self.backend,
                                 key_func=key_func,
                                 timeout=timeout,
                                 namespace=namespace,
                                 tags=tags,
                                 should_cache_fn=should_cache_fn,
                                 tag_prefix=self.tag_prefix
                                 )

    def invalidate_tag(self, tag):
        key = self.tag_prefix + tag
        self.backend.delete(key)

    def batch(self, keys_func=arguments_batch_keys_generator, timeout=3600, namespace=None):
        return lambda fn: Batch(fn, backend=self.backend,
                                keys_func=keys_func,
                                timeout=timeout,
                                namespace=namespace,
                                )
