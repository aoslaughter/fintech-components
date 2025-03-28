import scipy.optimize
from decimal import *

def xnpv(rate, values, dates):
    if rate <= -1.0:
        return float('inf')
    d0 = min(dates)
    npv = sum([vi / Decimal(1.0 + rate) ** ((di-d0).days / Decimal(365.0)) for vi, di in zip(values, dates)])

    return npv

def xirr(values, dates):
    try:
        return scipy.optimize.newton(lambda r: float(xnpv(r, values, dates)), 0.0)
    except RuntimeError:
        return scipy.optimize.brentq(lambda r: float(xnpv(r, values, dates)), -1.0, 1e10)