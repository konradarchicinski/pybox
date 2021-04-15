#ifndef EXPONENTIAL_DISTRIBUTION_H
#define EXPONENTIAL_DISTRIBUTION_H

#include "extern/src/distributions/distribution.h"

class ExponentialDistribution : public Distribution
{
public:
    ExponentialDistribution(double _lambda = 1.0);
    virtual ~ExponentialDistribution(){};

    double lambda;

    virtual double pdf(const double &x) const;
    virtual double cdf(const double &x) const;
    virtual double ppf(const double &q) const;

    virtual double mean() const;
    virtual double variance() const;
};

#endif