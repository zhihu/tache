#!/usr/bin/env python
# -*- coding: utf-8 -*-
import six


if six.PY2:
    basestring = basestring
else:
    basestring = (str, bytes)
