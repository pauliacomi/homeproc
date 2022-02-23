import math

__all__ = [
    'sauerbrey',
    'reverse_sauerbrey',
]

d = 0.51  # electrode diameter, cm
A = math.pi * (d / 2)**2  # electrode area, cm2
rho = 2.648  # quartz density, g/cm3
mu = 3.947e11  # shear modulus AT cut g /cm /s2


def sauerbrey(dF, F0):
    "Calculate mass (in mg) as a function of resonance frequency and base frequency (in Hz)."
    return (dF * A * math.sqrt(rho * mu) / (-2 * F0**2)) * 1000  # mass, mg


def reverse_sauerbrey(dm, F0):
    "Calculate resonance frequency change (in Hz) as a function of mass (in mg) and base frequency."
    return (-2 * dm * F0**2) / (A * math.sqrt(rho * mu) * 1000)
