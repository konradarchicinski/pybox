#ifndef NORMAL_DISTRIBUTION_H
#define NORMAL_DISTRIBUTION_H

#include "extern/src/distributions/distribution.h"

class NormalDistribution : public Distribution
{
public:
    NormalDistribution(double _mu = 0.0, double _sigma = 1.0);
    virtual ~NormalDistribution(){};

    double mu;
    double sigma;

    virtual double pdf(const double &x) const;
    virtual double cdf(const double &x) const;
    virtual double ppf(const double &q) const;

    virtual double mean() const;
    virtual double variance() const;
};

#endif