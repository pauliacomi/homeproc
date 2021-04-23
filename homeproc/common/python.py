"""
Module comprising python utilities.

@author: Dr. Paul Iacomi
@date: Jan 2021
"""

__all__ = [
    "pairwise",
]

from itertools import tee


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
