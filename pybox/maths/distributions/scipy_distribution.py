#!/usr/bin/env python
from pybox.maths.distributions import Distribution

import sys
from scipy import stats


class ScipyDistribution(Distribution):

    def __init__(self, settings):
        if settings['name'] == 'Normal':
            self._inner = getattr(sys.modules['scipy.stats'], 'norm')
        elif settings['name'] == 'T':
            self._inner = getattr(sys.modules['scipy.stats'], 't')
        elif settings['name'] == 'SkewedNormal':
            self._inner = getattr(sys.modules['scipy.stats'], 'skewnorm')
        elif settings['name'] == 'SkewedT':
            self._inner = getattr(sys.modules['scipy.stats'], 'nct')
        else:
            try:
                self._inner = getattr(sys.modules['scipy.stats'],
                                      settings['name'])
            except AttributeError:
                raise (('No SciPy distribution with the '
                        f'`{settings["name"]}` name'))

        if not isinstance(self._inner, stats.rv_continuous):
            raise ((f'Provided distribution called {settings["name"]}'
                    ' is not implemented.'))

        self.parameters = dict()

    def pdf(self, x, *args, **kwds):
        """Probability density function at x of the given RV."""
        return self._inner.pdf(x, *args, **kwds)

    def logpdf(self, x, *args, **kwds):
        """Log of the probability density function at x of the given RV."""
        return self._inner.logpdf(x, *args, **kwds)

    def cdf(self, x, *args, **kwds):
        """Cumulative distribution function of the given RV."""
        return self._inner.cdf(x, *args, **kwds)

    def logcdf(self, x, *args, **kwds):
        """Log of the cumulative distribution function at x of the given RV."""
        return self._inner.logcdf(x, *args, **kwds)

    def sf(self, x, *args, **kwds):
        """Survival function (1 - cdf) at x of the given RV."""
        return self._inner.sf(x, *args, **kwds)

    def logsf(self, x, *args, **kwds):
        """Log of the survival function of the given RV."""
        return self._inner.logsf(x, *args, **kwds)

    def ppf(self, q, *args, **kwds):
        """Percent point function (inverse of cdf) at q of the given RV."""
        return self._inner.ppf(q, *args, **kwds)

    def isf(self, q, *args, **kwds):
        """Inverse survival function (inverse of sf) at q of the given RV."""
        return self._inner.isf(q, *args, **kwds)

    def fit(self, data, *args, **kwds):
        """Return MLEs for shape (if applicable), location, and scale
        parameters from data.
        """
        return self._inner.fit(data, *args, **kwds)

    def initilize_starting_values(self, data):
        distribution_parameters = self._inner.shapes
        if distribution_parameters is not None:
            for distribution_parameter in distribution_parameters.split(', '):
                self.parameters[distribution_parameter] = 1.0
