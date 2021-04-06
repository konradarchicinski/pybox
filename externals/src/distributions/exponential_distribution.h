#ifndef EXPONENTIAL_DISTRIBUTION
#define EXPONENTIAL_DISTRIBUTION

#include "externals/src/distributions/distribution.h"

class ExponentialDistribution : public Distribution
{
public:
    double lambda;

    ExponentialDistribution(double _lambda = 1.0)
    {
        left_support = 0.0;

        lambda = _lambda;
    }
    ~ExponentialDistribution(){};

    double pdf(double x);
    double cdf(double x);
    double ppf(double q);

    double mean();
    double variance();
};

#endif