#!/usr/bin/env python
from pybox.maths.time_series.mean_process import MeanProcess


class ConstantMean(MeanProcess):

    def residuals(self, data, estimates):
        return data - estimates['mean_constant']
