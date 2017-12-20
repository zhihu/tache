# Tag 详细用法

.. note:: 不建议用来缓存细粒度接口，每次读取时会多取一次 tag， 因此对接口缓存的请求量会放大一倍

## 可以有多个tag

```
@cache.cached(tags=["a:{0}", "b:{1}", "c"])
def add(a, b):
    return a + b + random.randint(1,100)
```

## tag 可以是函数

接受参数 `*args`, `**kwargs`, 返回字符串。由于默认的
key_generator 不接受 kwargs, 通常用不上这个参数。

```
@cache.cached(tags=[lambda *args, **kwargs: "add:{0}".format(args[0] + args[1])])
def add(a, b):
    return a + b + random.randint(1,100)

add(5, 6)
add(4, 7)
add(5, 8)
add.invalidate_tag("add:11") # 前两个函数的缓存失效
```
