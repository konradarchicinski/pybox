#ifndef CHI_SQUARE_DISTRIBUTION
#define CHI_SQUARE_DISTRIBUTION

#include "externals/src/distributions/gamma_distribution.h"

class ChiSquareDistribution : public Distribution
{
private:
    GammaDistribution gamma_distribution;

public:
    int k;

    ChiSquareDistribution(int _k = 2) : gamma_distribution(_k / 2.0, 2.0)
    {
        left_support = 0.0;

        k = _k;
    }
    ~ChiSquareDistribution(){};

    double pdf(double x) { return gamma_distribution.pdf(x); }
    double cdf(double x) { return gamma_distribution.cdf(x); }

    double mean() { return gamma_distribution.mean(); }
    double variance() { return gamma_distribution.variance(); }
};

#endif