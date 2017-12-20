# Tache
[![Build Status](https://travis-ci.org/zhihu/tache.svg?branch=master)](https://travis-ci.org/zhihu/tache)
[![Pypi Status](https://img.shields.io/pypi/v/tache.svg)](https://pypi.python.org/pypi/tache)

Tache 是一个 Python 的缓存框架。它基于如下的目标而设计:

* 同时支持 Python2 和 Python3
* 支持缓存普通函数/实例方法/类方法/静态方法
* 支持 Batch 批量缓存
* 支持基于 Tag 的缓存和失效
* 支持基于参数显式声明 key 格式

 [Documention](http://zhihu.github.io/tache)
 
 [项目地址](https://github.com/zhihu/tache)


Contents
---------
* [Tag 详细用法](docs/advance_tag.md)
* [使用关键字参数](docs/use_kwargs.md)
* [Cache 空值与缓存穿透](docs/cache_null_and_miss.md)


## Features

* 默认缓存空值，防止穿透
* 基于tag 批量失效缓存
* batch 批量缓存
* 支持 `YAML` `JSON` `PICKLE` 多种 Backend Serializer

## Getting Started

* 基本用法

```
import random
import fakeredis
from tache import RedisCache

redis_client = fakeredis.FakeStrictRedis()
cache = RedisCache(conn=redis_client, format="JSON")

@cache.cached()
def add(a, b):
    return a + b + random.randint(1,100)

result1 = add(5, 6)
# 缓存生效值不变
assert add(5, 6) == result1
# 失效缓存
add.invalidate(5, 6)
assert add(5, 6) != result1
```

* 基于 tag 的批量缓存失效

tag 可以是固定也可以是动态的，其中动态参数代表在函数中的参数位置。
失效某个 tag 时，代表这个函数下拥有相同 tag 的缓存全部失效。

```
@cache.cached(tags=["a:{0}"])
def add(a, b):
    return a + b + random.randint(1,100)

result1 = add(5, 6) 
result2 = add(5, 7)
add.invalidate_tag("a:5")
assert result1 != add(5, 6) 
assert result2 != add(5, 7)
```


* refresh 刷新缓存

当调用refresh 时，将会重新刷新缓存并返回最新值。


```
class A(object):

    def __init__(self):
        self.extra = 0

    @cache.cached()
    def add(self, a, b):
        self.extra += 1
        return a + b + self.extra

a = A()
assert a.add(5, 6) == 12
assert a.extra == 1
assert a.add.refresh(5, 6) == 13
assert a.extra == 2
```

* batch 缓存模式

```
@cache.batch()
def get_comments(*comment_ids):
    return [get_comment(c) for c in comment_ids]

get_comments(1,2,3,4,5) # no cache, 调用完毕全部缓存
get_comments(2,3,4,5,6) # 2,3,4,5 从缓存中取，6 在调用完缓存
get_comments.invalidate(3,4,5) # 失效 3,4,5 的缓存
```

* 显式声明 Key

Tache 允许你显式声明 Key 的生成规则， 不论代码如何重构, 生成的 key 都不会改变。

```
class B:

    def __init__(self):
        self.count = 0

    @cache.cached("counter.B.add|{0}-{1}")
    def add(self, a, b):
        self.count += 1
        return a + b + self.count
```


## Notice

* 支持 `classmethod/staticmethod` 描述符, 但在使用 `classmethod` 时目前必须把
`classmethod` 放在内层


```
class AC(object):

    @cache.cached()
    @classmethod
    def add(cls, a, b):
        return a + b + random.randint(1,100)
```

* 设置 namespace, 处理对象属性修改的问题

key 的生成规则默认为 `namespace:module.classname.func|arg1-arg2|tag1-tag2`。
其中 `namespace` 为空, `classname` 不存在时也为空。

```
class A(object):
    @cache.cache(namespace="v1")
    def add(self, a, b):
        return db.execute(sql).fetchone()
```

这个例子中，如果数据库字段发生更改，可以通过修改 namespace 的方式，让新老代码使用不同的缓存结果。
