#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

import fakeredis
from tache import RedisCache
from tache.utils import kwargs_key_generator


def test_cache_function():
    r = fakeredis.FakeStrictRedis()
    r.flushall()
    cache = RedisCache(conn=r)

    class A:

        def __init__(self):
            self.count = 0

        @cache.cached()
        def add(self, a, b):
            self.count += 1
            return a + b + self.count

    class B:

        def __init__(self):
            self.count = 0

        @cache.cached('tests.test_redis_cache.A.add|{0}-{1}')
        def add_explicit(self, a, b):
            self.count += 1
            return a + b + self.count

    a = A()
    assert a.add(5, 6) == 12
    assert a.add(5, 6) == 12
    assert a.count == 1
    a.add.invalidate(5, 6)
    assert a.add(5, 6) == 13
    assert a.count == 2
    assert a.add.refresh(5, 6) == 14
    assert a.count == 3
    assert a.add(5, 6) == 14
    b = B()
    assert b.add_explicit(5, 6) == 14


def test_cache_kwargs():
    r = fakeredis.FakeStrictRedis()
    r.flushall()
    cache = RedisCache(conn=r)

    class A(object):

        def __init__(self):
            self.count = 0

        @cache.cached(key_func=kwargs_key_generator)
        def add(self, a, b):
            self.count += 1
            return a + b + self.count

    class B(object):

        def __init__(self):
            self.count = 0

        @cache.cached("tests.test_redis_cache.A.add|('a', {a}),('b', {b})")
        def add_explicit(self, a, b):
            self.count += 1
            return a + b + self.count

    a = A()
    assert a.add(a=5, b=6) == 12
    assert a.add(a=5, b=6) == 12
    assert a.count == 1
    a.add.invalidate(a=5, b=6)
    assert a.add(a=5, b=6) == 13
    assert a.count == 2
    assert a.add.refresh(a=5, b=6) == 14
    assert a.count == 3
    assert a.add(a=5, b=6) == 14
    b = B()
    assert b.add_explicit(a=5, b=6) == 14


def test_cache_None():
    r = fakeredis.FakeStrictRedis()
    r.flushall()
    cache = RedisCache(conn=r)

    global i
    i = 0

    @cache.cached()
    def incr():
        global i
        i += 1

    incr()
    assert i == 1
    incr()
    assert i == 1
    incr.invalidate()
    incr()
    assert i == 2


def test_not_cache_None():
    r = fakeredis.FakeStrictRedis()
    r.flushall()
    cache = RedisCache(conn=r)

    global i
    i = 0

    @cache.cached(should_cache_fn=lambda value: value is not None)
    def incr(by):
        global i
        i += 1
        return by

    incr(None)
    incr(None)
    assert i == 2
    incr(1)
    incr(1)
    assert i == 3


def test_cache_classmethod():
    r = fakeredis.FakeStrictRedis()
    r.flushall()
    cache = RedisCache(conn=r)

    class AC(object):

        count = 0

        @cache.cached()
        @classmethod
        def add(cls, a, b):
            return a + b + random.randint(1, 100)

        @cache.cached()
        @classmethod
        def plus(cls, a, b):
            cls.__name__ = 'AD'
            return a + b + random.randint(1, 100)

    assert AC.add(3, 4) == AC.add(3, 4) == AC().add(3, 4)
    assert AC.plus(3, 4) != AC.plus(3, 4)


def test_cache_staticmethod():
    r = fakeredis.FakeStrictRedis()
    r.flushall()
    cache = RedisCache(conn=r)

    class AS(object):

        count = 0

        @cache.cached()
        @staticmethod
        def add(a, b):
            return a + b + random.randint(1, 100)

    assert AS.add(3, 4) == AS.add(3, 4) == AS().add(3, 4)
