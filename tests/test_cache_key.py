#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from tache.utils import (arguments_key_generator, kwargs_key_generator,
                         arguments_batch_keys_generator)


def add(a, b):
    return a + b + random.randint(0, 100)


class A:
    def plus(self, a, b):
        return a + b + random.randint(0, 100)


def test_function_key():
    key = arguments_key_generator("prefix", add, 5, 6)
    assert key == "prefix:tests.test_cache_key.add|5-6"
    key = arguments_key_generator("prefix", add, 5, u"测试")
    assert key == "prefix:tests.test_cache_key.add|5-测试"
    key = arguments_key_generator(None, A().plus, 5, 6)
    assert key == "tests.test_cache_key.A.plus|5-6"


def test_kwargs_key():
    key = kwargs_key_generator("prefix", add, a=5, b=6)
    assert key == "prefix:tests.test_cache_key.add|('a', 5),('b', 6)"
    key = kwargs_key_generator(None, add, a=5, b=6)
    assert key == "tests.test_cache_key.add|('a', 5),('b', 6)"


def test_batch_key():
    keys = arguments_batch_keys_generator("prefix", add, 5, 6)
    assert keys == ['prefix:tests.test_cache_key.add|5', 'prefix:tests.test_cache_key.add|6']
