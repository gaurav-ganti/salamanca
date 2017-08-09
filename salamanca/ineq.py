from copy import deepcopy

import numpy as np

from scipy.stats import norm, lognorm
from scipy.special import erf, erfinv

# empirical limits with gini = 0.99
MAX_THEIL = 6.64


def gini_to_std(g):
    """$$\sigma = 2 \erf^{-1}(g)$$"""
    return 2.0 * erfinv(g)


def std_to_gini(s):
    """$$g = \erf(\frac{1}{2} \sigma)$$"""
    return erf(0.5 * s)


def theil_to_std(t):
    """$$\sigma = \sqrt{2t}$$"""
    return (2 * t) ** 0.5


def std_to_theil(s):
    """$$t = \frac{1}{2}\sigma^2$$"""
    return s ** 2 / 2.0


def theil_empirical_constants():
    """
    These quadractic constants were established by Narasimha to translate between
    Thiel values calculated from deciles to those calculated from Ginis
    """
    return 0.216, 0.991, 0.003


def gini_to_theil(g, empirical=False):
    """Translate gini to theil

    $$t(g) = \sqrt{2} \Phi^{-1} \left( \frac{1 + g}{2} \right)$$

    Where $$\Phi$$ is cumulative distribution function (CDF) of the standard
    normal distribution.

    Parameters
    ----------
    g : numeric or array-like
        gini coefficient(s)
    empirical : bool, optional, default: False
        whether to use empirical relationship for theil
    """
    if not (np.all(g > 0) and np.all(g < 1)):
        raise ValueError('Gini not within (0, 1)')

    s = gini_to_std(g)
    t = std_to_theil(s)
    if empirical:
        # quadratic method root finding
        a, b, c = theil_empirical_constants()
        t = (-b + (b ** 2 - 4 * a * (c - t)) ** 0.5) / (2 * a)

    if not (np.all(t < MAX_THEIL) and np.all(t > 0)):
        raise ValueError('Theil not within (0, 2.88)')
    return t


def theil_to_gini(t, empirical=False):
    """Translate theil to gini

    $$t(g) = \sqrt{2} \Phi^{-1} \left( \frac{1 + g}{2} \right)$$

    Where $$\Phi$$ is cumulative distribution function (CDF) of the standard
    normal distribution.

    Parameters
    ----------
    t : numeric or array-like
        theil coefficient(s)
    empirical : bool, optional, default: False
        whether to use empirical relationship for theil
    """
    if not (np.all(t < MAX_THEIL) and np.all(t > 0)):
        raise ValueError('Theil not within (0, 2.88)')

    if empirical:
        a, b, c = theil_empirical_constants()
        t = a * t ** 2 + b * t + c
    s = theil_to_std(t)
    g = std_to_gini(s)

    if not (np.all(g > 0) and np.all(g < 1)):
        raise ValueError('Gini not within (0, 1)')
    return g


class AttrObject(object):
    """Simple base class to have dictionary-like attributes attached to an 
    object
    """

    def __init__(self, **kwargs):
        self.update(copy=False, **kwargs)

    def update(self, copy=True, override=True, **kwargs):
        """Update attributes.

        Parameters
        ----------
        copy : bool, optional, default: True
            operate on a copy of this object
        override : bool, optional, default: True
            overrides attributes if they already exist on the object
        """
        x = deepcopy(self) if copy else self
        for k, v in kwargs.items():
            if override or getattr(x, k, None) is None:
                setattr(x, k, v)
        return x


class LogNormalData(AttrObject):
    """Object for storing and updating LogNormal distribution data"""

    def _get(self, x):
        return getattr(self, x, None)

    def add_defaults(self, copy=True):
        # add new defaults for kwargs here
        defaults = {
            'inc': 1,
            'mean': True,
            'gini': None,
            'theil': None,
        }
        return self.update(copy=copy, override=False, **defaults)

    def check(self):
        x = ('theil', 'gini')
        bad = all(self._get(_) is None for _ in x)
        if bad:
            raise ValueError('Must use either theil or gini')
        bad = all(self._get(_) is not None for _ in x)
        if bad:
            raise ValueError('Cannot use both theil and gini')

        x = ('inc', 'mean')
        for _ in x:
            if self._get(_) is None:
                raise ValueError('Must declare value for ' + _)
        return self


class LogNormal(object):
    """An interfrace to the log-normal distribution.

    For mathematical descriptions see scipy.stats.lognorm.

    Parameters
    ----------
    inc  : numeric, optional, default: 1
    mean : bool, optional, default: True
        whether income is representative of mean (True) or median (False)
    gini : numeric, optional
    theil : numeric, optional
    """

    def __init__(self, **kwargs):
        self.init_data = LogNormalData(**kwargs)

    def params(self, **kwargs):
        """Returns (shape, scale) tuple for use in scipy.stats.lognorm"""
        data = (
            self.init_data
            .update(**kwargs)
            .add_defaults(copy=True)
            .check()
        )

        shape = gini_to_std(data.gini) if data.theil is None \
            else theil_to_std(data.theil)
        # scale assumes a median value, adjust is made if income is mean income
        scale = np.exp(np.log(data.inc) - shape ** 2 / 2) if data.mean \
            else data.inc
        return shape, scale

    def ppf(self, x, **kwargs):
        shape, scale = self.params(**kwargs)
        return lognorm.cdf(x, shape, scale=scale)

    def cdf(self, x, **kwargs):
        shape, scale = self.params(**kwargs)
        return lognorm.cdf(x, shape, scale=scale)

    def lorenz(self, x, **kwargs):
        """The Lorenz curve for log-normal distributions is defined as:

        $$L(x) = \phi \left( \phi^{-1} (x) - \sigma \right)$$
        """
        shape, scale = self.params(**kwargs)
        return norm.cdf(norm.ppf(x) - shape)

    def mean(self, **kwargs):
        shape, scale = self.params(**kwargs)
        return lognorm.mean(shape, scale=scale)

    def median(self, **kwargs):
        shape, scale = self.params(**kwargs)
        return lognorm.median(shape, scale=scale)

    def var(self, **kwargs):
        shape, scale = self.params(**kwargs)
        return lognorm.var(shape, scale=scale)

    def std(self, **kwargs):
        shape, scale = self.params(**kwargs)
        return lognorm.std(shape, scale=scale)