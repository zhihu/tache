# 使用关键字参数

在同时使用位置参数和关键字参数时，生成的 key 很难在较小的代价下保证一致。如对下面这个函数:

```
def f(a, b=None):
    pass
```

在我们的缓存库 zmemcache 中，使用 `f(2, 3)` 和 `f(a=2, b=3)` 这两个等价的函数调用会生成两个 key,
需要分别进行缓存和失效。

基于最小惊讶的原则，我们希望同一函数在所有使用的地方都按照一致的方式调用。默认我们使用的是位置参数，
因为它的使用方式单一，顺序确定，生成的 key 比较短。开源的较出名的缓存库，如 beaker，dogpile 等也都是
默认使用位置参数。


##  基本用法

虽然希望整体风格都能统一，但如果出于个人的偏爱，更喜欢用关键字参数，这里也给予了支持，需要做的是替换
cache 装饰器的 key_func 函数。

```
from tache.utils import kwargs_key_generator

@cache.cached(key_func=kwargs_key_generator)
def add(a, b):
    return a + b
```

使用了上述 key_func 后，`add` 函数便只能使用关键字参数来调用了。 失效也要用关键字参数失效:

```
add.invalidate(a=x, b=x)
```

包括刷新缓存:

```
add.refresh(a=x, b=x)
```

##  tag 用法的改变

因为不再传入位置参数，现在 tag 的用法也要相应改变。

单个 tag:

```
@cache.cached(key_func=kwargs_key_generator, tags=["a:{a}"])
def add(a, b):
    return a + b
```

多 tag:

```
@cache.cached(key_func=kwargs_key_generator, tags=["a:{a}", "b:{b}"])
def add(a, b):
    return a + b
```

基于函数的 tag:

```
@cache.cached(key_func=kwargs_key_generator, tags=[lambda *args, **kwargs: "add:{0}".format(kwargs['a'] + kwargs['b'])])
def add(a, b):
    return a + b
```

## 使用 batch ?

目前没有什么办法来支持，只能使用位置参数
