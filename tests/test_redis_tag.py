#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

import fakeredis
from tache import RedisCache
from tache.utils import kwargs_key_generator


def test_tag_cache_function():
    r = fakeredis.FakeStrictRedis()
    r.flushall()
    cache = RedisCache(conn=r)

    @cache.cached(tags=["add:{0}"])
    def add(a, b):
        return a + b + random.randint(1, 10000)

    add_result1 = add(5, 6)
    add_result2 = add(5, 7)
    add_result3 = add(5, 8)
    add_result4 = add(6, 8)

    # cache 生效
    assert add(5, 6) == add_result1
    assert add(5, 7) == add_result2
    assert add(5, 8) == add_result3
    assert add(6, 8) == add_result4

    # 精确失效
    add.invalidate(5, 6)
    assert add(5, 6) != add_result1
    assert add(5, 7) == add_result2
    assert add(5, 8) == add_result3
    assert add(6, 8) == add_result4

    # 批量失效
    add.invalidate_tag("add:5")
    assert add(5, 7) != add_result2
    assert add(5, 8) != add_result3
    assert add(6, 8) == add_result4


def test_tag_cache_kwargs_function():
    r = fakeredis.FakeStrictRedis()
    r.flushall()
    cache = RedisCache(conn=r)

    @cache.cached(key_func=kwargs_key_generator, tags=["add:{a}"])
    def add(a, b):
        return a + b + random.randint(1, 10000)

    add_result1 = add(a=5, b=6)
    add_result2 = add(a=5, b=7)
    add_result3 = add(a=5, b=8)
    add_result4 = add(a=6, b=8)

    # cache 生效
    assert add(a=5, b=6) == add_result1
    assert add(a=5, b=7) == add_result2
    assert add(a=5, b=8) == add_result3
    assert add(a=6, b=8) == add_result4

    # 精确失效
    add.invalidate(a=5, b=6)
    assert add(a=5, b=6) != add_result1
    assert add(a=5, b=7) == add_result2
    assert add(a=5, b=8) == add_result3
    assert add(a=6, b=8) == add_result4

    # 批量失效
    add.invalidate_tag("add:5")
    assert add(a=5, b=7) != add_result2
    assert add(a=5, b=8) != add_result3
    assert add(a=6, b=8) == add_result4


def test_cache_method():
    r = fakeredis.FakeStrictRedis()
    r.flushall()
    cache = RedisCache(conn=r)

    class A(object):
        @cache.cached(tags=["add:{0}"])
        def add(self, a, b):
            return a + b + random.randint(1, 10000)

        @cache.cached(tags=["plus:{0}"])
        @classmethod
        def plus(cls, a, b):
            return a + b + random.randint(1, 10000)

    plus_result1 = A.plus(5, 6)
    assert A.plus(5, 6) == plus_result1
    add_result1 = A().add(5, 6)
    assert A().add(5, 6) == add_result1


def test_multi_tag():
    r = fakeredis.FakeStrictRedis()
    r.flushall()
    cache = RedisCache(conn=r)

    class A(object):
        @cache.cached(tags=["a:{0}", "b:{1}", "c"])
        def add(self, a, b):
            return a + b + random.randint(1, 10000)

    add_result1 = A().add(5, 6)
    add_result2 = A().add(5, 7)
    add_result3 = A().add(1, 8)
    add_result4 = A().add(1, 8)
    add_result5 = A().add(2, 9)
    A().add.invalidate_tag("a:5")
    A().add.invalidate_tag("b:8")
    assert add_result1 != A().add(5, 6)
    assert add_result2 != A().add(5, 7)
    assert add_result3 != A().add(1, 8)
    assert add_result4 != A().add(1, 8)
    assert add_result5 == A().add(2, 9)
    A().add.invalidate_tag("c")
    assert add_result5 != A().add(2, 9)


def test_multi_tag_kwargs():
    r = fakeredis.FakeStrictRedis()
    r.flushall()
    cache = RedisCache(conn=r)

    class A(object):
        @cache.cached(key_func=kwargs_key_generator, tags=["a:{a}", "b:{b}", "c"])
        def add(self, a, b):
            return a + b + random.randint(1, 10000)

    add_result1 = A().add(a=5, b=6)
    add_result2 = A().add(a=5, b=7)
    add_result3 = A().add(a=1, b=8)
    add_result4 = A().add(a=1, b=8)
    add_result5 = A().add(a=2, b=9)
    A().add.invalidate_tag("a:5")
    A().add.invalidate_tag("b:8")
    assert add_result1 != A().add(a=5, b=6)
    assert add_result2 != A().add(a=5, b=7)
    assert add_result3 != A().add(a=1, b=8)
    assert add_result4 != A().add(a=1, b=8)
    assert add_result5 == A().add(a=2, b=9)
    A().add.invalidate_tag("c")
    assert add_result5 != A().add(a=2, b=9)


def test_function_tag():
    r = fakeredis.FakeStrictRedis()
    r.flushall()
    cache = RedisCache(conn=r)

    @cache.cached(tags=[lambda *args, **kwargs: "add:{0}".format(args[0] + args[1])])
    def add(a, b):
        return a + b + random.randint(1, 10000)

    add_result1 = add(5, 6)
    add_result2 = add(4, 7)
    add_result3 = add(5, 8)

    # cache 生效
    assert add(5, 6) == add_result1
    assert add(4, 7) == add_result2
    assert add(5, 8) == add_result3

    add.invalidate_tag("add:11")
    assert add(5, 6) != add_result1
    assert add(4, 7) != add_result2
    assert add(5, 8) == add_result3


def test_function_tag_kwargs():
    r = fakeredis.FakeStrictRedis()
    r.flushall()
    cache = RedisCache(conn=r)

    @cache.cached(key_func=kwargs_key_generator, tags=[lambda *args, **kwargs: "add:{0}".format(kwargs['a'] + kwargs['b'])])
    def add(a, b):
        return a + b + random.randint(1, 10000)

    add_result1 = add(a=5, b=6)
    add_result2 = add(a=4, b=7)
    add_result3 = add(a=5, b=8)

    # cache 生效
    assert add(a=5, b=6) == add_result1
    assert add(a=4, b=7) == add_result2
    assert add(a=5, b=8) == add_result3

    add.invalidate_tag("add:11")
    assert add(a=5, b=6) != add_result1
    assert add(a=4, b=7) != add_result2
    assert add(a=5, b=8) == add_result3


def test_global_tag():
    r = fakeredis.FakeStrictRedis()
    r.flushall()
    cache = RedisCache(conn=r)

    @cache.cached(tags=["add:{0}"])
    def add(a, b):
        return a + b + random.randint(1, 10000)

    @cache.cached(tags=["add:{0}"])
    def add2(a, b):
        return a + b + random.randint(1, 10000)

    add_result1 = add(5, 6)
    add_result2 = add(5, 7)
    add2_result1 = add2(5, 6)

    # cache 生效
    assert add(5, 6) == add_result1
    assert add(5, 7) == add_result2
    assert add2(5, 6) == add2_result1

    # cache 失效，影响 add2
    add.invalidate_tag("add:5")
    assert add(5, 6) != add_result1
    assert add(5, 7) != add_result2
    assert add2(5, 6) != add2_result1

    # 使用 global invalidate tag
    add_result1 = add(5, 6)
    add_result2 = add(5, 7)
    add2_result1 = add2(5, 6)
    assert add(5, 6) == add_result1
    assert add(5, 7) == add_result2
    assert add2(5, 6) == add2_result1
    cache.invalidate_tag("add:5")
    assert add(5, 6) != add_result1
    assert add(5, 7) != add_result2
    assert add2(5, 6) != add2_result1
