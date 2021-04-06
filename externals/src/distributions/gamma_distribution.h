#ifndef GAMMA_DISTRIBUTION
#define GAMMA_DISTRIBUTION

#include "externals/src/distributions/distribution.h"

class GammaDistribution : public Distribution
{
public:
    double k;
    double theta;

    GammaDistribution(double _k = 2.0, double _theta = 1.0)
    {
        left_support = 0.0;

        k = _k;
        theta = _theta;
    }
    ~GammaDistribution(){};

    double pdf(double x);
    double cdf(double x);

    double mean();
    double variance();
};

#endif