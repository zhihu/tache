#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
from .backend import RedisBackend
from .tache import Tache

RedisCache = functools.partial(Tache, RedisBackend)

__all__ = ['RedisCache']
