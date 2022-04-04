import math
import numpy

# NaCl Birch-Murnaghan EOS parameters
p_nacl = {
    "v0": 179.425,
    "b0": 23.83,
    "b0p": 5.09,
}

# The Use of Quartz as an Internal Pressure Standard in High-Pressure
# Crystallography R. J. ANGEL, D. R. ALLAN,5" R. MILETICH AND t. W. FINGER +
# Bayerisches Geoinstitut, Universitaet Bayreuth, D-95440, Bayreuth, Germany.
# E-mail: ross.angel@uni-bayreuth.de

# Quartz Vinot EOS parameters
p_qtz = {
    "v0": 112.981,
    "b0": 37.12,
    "b0p": 5.99,
}


def calc_uc_vol_base(a, b, c, al, be, ga):
    """Calculate UC vol from individual params."""

    # convert to rad
    al = al / 180 * math.pi
    be = (180 - be) / 180 * math.pi
    ga = ga / 180 * math.pi

    return a * b * c * (
        math.sqrt((1 - math.cos(al)**2 - math.cos(be)**2 - math.cos(ga)**2) +
                  2 * math.cos(al) * math.cos(be) * math.cos(ga))
    )


def calc_uc_err_base(a, b, c, al, be, ga, da, db, dc, dal, dbe, dga):
    """Calculate UC vol error from individual params."""

    # convert to rad
    al = al / 180 * math.pi
    be = (180 - be) / 180 * math.pi
    ga = ga / 180 * math.pi

    ang = math.sqrt((1 - math.cos(al)**2 - math.cos(be)**2 - math.cos(ga)**2) +
                    2 * math.cos(al) * math.cos(be) * math.cos(ga))

    return math.sqrt((a * b * ang * dc)**2 + (a * c * ang * db)**2 + (b * c * ang * da)**2)


def calc_uc_vol(uc_dict):
    """Calculate UC vol from a dict of params."""
    return calc_uc_vol_base(
        uc_dict['a'],
        uc_dict['b'],
        uc_dict['c'],
        uc_dict['alpha'],
        uc_dict['beta'],
        uc_dict['gamma'],
    )


def calc_uc_err(uc_dict, su_dict):
    """Calculate UC vol error from a dict of params and uncertainty."""
    return calc_uc_err_base(
        uc_dict['a'],
        uc_dict['b'],
        uc_dict['c'],
        uc_dict['alpha'],
        uc_dict['beta'],
        uc_dict['gamma'],
        su_dict['a'],
        su_dict['b'],
        su_dict['c'],
        su_dict['alpha'],
        su_dict['beta'],
        su_dict['gamma'],
    )


def bm_eos(v, v0, b0, b0p):
    """Birch-Murnaghan EOS"""
    vr = v0 / v
    return (1.5 * b0 * (vr**(7 / 3) - vr**(5 / 3)) * (1 + 0.75 * (b0p - 4) * (vr**(2 / 3) - 1)))


def d_bm_eos(v, v0, b0, b0p):
    """Numerical differentiation of Birch-Murnaghan EOS"""
    return (
        b0 * v0 * (
            v0**2 * (13.5 - 3.375 * b0p) - 1.875 * (b0p - 5.33333) * v**2 *
            (v0 / v)**(2 / 3) + 5.25 * (b0p - 4.66667) * v0 * v * (v0 / v)**(1 / 3)
        )
    ) / v**4


def v_eos(v, v0, b0, b0p):
    """Vinot equation of state"""
    n = (v / v0)**(1 / 3)
    return 3 * b0 * (1 - n) / n**2 * numpy.exp(1.5 * (b0p - 1) * (1 - n))


def d_v_eos(v, v0, b0, b0p):
    """Numerical differentiation of Vinot EOS"""
    return (
        b0 * (-1.5 * (b0p - 1) * ((v / v0)**(1 / 3) - 1)) * (
            1.5 * b0p * (v / v0)**(2 / 3) - 1.5 * b0p * (v / v0)**(1 / 3) - 1.5 *
            (v / v0)**(2 / 3) + 2.5 * (v / v0)**(1 / 3) - 2
        )
    ) / (v * (v / v0)**(2 / 3))


def norm(intensity):
    """Normalize"""
    return (intensity - intensity.mean()) / (intensity.max() - intensity.min())