#ifndef NORMAL_DISTRIBUTION
#define NORMAL_DISTRIBUTION

#include "externals/src/distributions/distribution.h"

class NormalDistribution : public Distribution
{
public:
    double mu;
    double sigma;

    NormalDistribution(double _mu = 0.0, double _sigma = 1.0)
    {
        mu = _mu;
        sigma = _sigma;
    }
    ~NormalDistribution(){};

    double pdf(double x);
    double cdf(double x);
    double ppf(double q);

    double mean();
    double variance();
};

#endif