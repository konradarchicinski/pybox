#!/usr/bin/env python
from pybox.maths.time_series.mean_process import MeanProcess


class AutoRegressiveMovingAverage(MeanProcess):

    def __init__(self, settings=dict()):
        super().__init__(settings)

        if 'AutoRegressiveLags' not in settings:
            self.p = [1]
        else:
            self.p = settings['AutoRegressiveLags']
        if 'MovingAverageLags' not in settings:
            self.q = [1]
        else:
            self.q = settings['MovingAverageLags']

        for i, lag in enumerate(self.p):
            self.parameters[f'ar{lag}'] = 0.5**(i+1)
        for i, lag in enumerate(self.q):
            self.parameters[f'ma{lag}'] = 0.5**(i+i)

        self.max_ar_lag = 0 if not self.p else max(self.p)
        self.max_ma_lag = 0 if not self.q else max(self.q)

    def residuals(self, data, estimates):
        ar_residuals = data[self.max_ar_lag:] - estimates['mean_constant']

        for lag in self.p:
            ar_residuals -= (
                estimates[f'ar{lag}'] *
                data[self.max_ar_lag-lag: -lag])

        ma_residuals = ar_residuals[self.max_ma_lag:]
        for lag in self.q:
            ma_residuals -= (
                estimates[f'ma{lag}'] *
                ar_residuals[self.max_ma_lag-lag: -lag])

        return ma_residuals
