#ifndef GAMMA_DISTRIBUTION_H
#define GAMMA_DISTRIBUTION_H

#include "extern/src/distributions/distribution.h"

class GammaDistribution : public Distribution
{
public:
    GammaDistribution(double _k = 2.0, double _theta = 1.0);
    virtual ~GammaDistribution(){};

    double k;
    double theta;

    virtual double pdf(const double &x) const;
    virtual double cdf(const double &x) const;

    virtual double mean() const;
    virtual double variance() const;
};

#endif