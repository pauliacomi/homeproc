import math
import functools

__all__ = [
    'sauerbrey',
    'reverse_sauerbrey',
]

d = 0.51  # electrode diameter, cm
rho = 2.648  # quartz density, g/cm3
mu = 3.947e11  # shear modulus AT cut g /cm /s2


@functools.cache
def area(de):
    """electrode area, cm2"""
    return math.pi * (de / 2)**2


def sauerbrey(dF, F0, de=d):
    "Calculate mass (in mg) as a function of resonance frequency and base frequency (in Hz)."
    return (dF * area(de) * math.sqrt(rho * mu) / (-2 * F0**2)) * 1000


def reverse_sauerbrey(dm, F0, de=d):
    "Calculate resonance frequency change (in Hz) as a function of mass (in mg) and base frequency."
    return (-2 * dm * F0**2) / (area(de) * math.sqrt(rho * mu) * 1000)
