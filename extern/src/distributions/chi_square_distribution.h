#ifndef CHI_SQUARE_DISTRIBUTION_H
#define CHI_SQUARE_DISTRIBUTION_H

#include "extern/src/distributions/gamma_distribution.h"

class ChiSquareDistribution : public Distribution
{
public:
    ChiSquareDistribution(int _k = 2);
    virtual ~ChiSquareDistribution(){};

    int k;

    virtual double pdf(const double &x) const;
    virtual double cdf(const double &x) const;

    virtual double mean() const;
    virtual double variance() const;

private:
    GammaDistribution gamma_distribution;
};

#endif