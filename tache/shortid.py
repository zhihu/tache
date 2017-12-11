#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import random

#: Epoch for simpleflake timestamps, starts at the year 2000
SIMPLEFLAKE_EPOCH = 946702800


SIMPLEFLAKE_RANDOM_LENGTH = 16
SIMPLEFLAKE_TIMESTAMP_SHIFT = 8



def simpleflake(timestamp=None, random_bits=None, epoch=SIMPLEFLAKE_EPOCH):
    """Generate a 64 bit, roughly-ordered, globally-unique ID."""
    second_time = timestamp if timestamp is not None else time.time()
    second_time -= epoch
    millisecond_time = int(second_time * 1000)

    randomness = random.SystemRandom().getrandbits(SIMPLEFLAKE_RANDOM_LENGTH)
    randomness = random_bits if random_bits is not None else randomness

    flake = (millisecond_time << SIMPLEFLAKE_TIMESTAMP_SHIFT) + randomness

    return flake


class BaseConverter(object):
    """
    Convert numbers from base 10 integers to base X strings and back again.

    Sample usage:

    >>> base20 = BaseConverter('0123456789abcdefghij')
    >>> base20.from_decimal(1234)
    '31e'
    >>> base20.to_decimal('31e')
    1234
    """
    decimal_digits = "0123456789"

    def __init__(self, digits):
        self.digits = digits

    def from_decimal(self, i):
        return self.convert(i, self.decimal_digits, self.digits)

    def to_decimal(self, s):
        return int(self.convert(s, self.digits, self.decimal_digits))

    def convert(number, fromdigits, todigits):
        # Based on http://code.activestate.com/recipes/111286/
        if str(number)[0] == '-':
            number = str(number)[1:]
            neg = 1
        else:
            neg = 0

        # make an integer out of the number
        x = 0
        for digit in str(number):
            x = x * len(fromdigits) + fromdigits.index(digit)

        # create the result in base 'len(todigits)'
        if x == 0:
            res = todigits[0]
        else:
            res = ""
            while x > 0:
                digit = x % len(todigits)
                res = todigits[digit] + res
                x = int(x / len(todigits))
            if neg:
                res = '-' + res
        return res
    convert = staticmethod(convert)


base62 = BaseConverter(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz'
)


def short_id():
    flake = simpleflake()
    return base62.from_decimal(flake)


if __name__ == "__main__":
    print(short_id(), len(short_id()))
