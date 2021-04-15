#include "extern/src/maths/special_functions.h"
#include "extern/src/distributions/chi_square_distribution.h"

ChiSquareDistribution::ChiSquareDistribution(int _k)
    : gamma_distribution(_k / 2.0, 2.0)
{
    left_support = 0.0;

    k = _k;
}

double ChiSquareDistribution::pdf(const double &x) const
{
    return gamma_distribution.pdf(x);
}
double ChiSquareDistribution::cdf(const double &x) const
{
    return gamma_distribution.cdf(x);
}

double ChiSquareDistribution::mean() const
{
    return gamma_distribution.mean();
}
double ChiSquareDistribution::variance() const
{
    return gamma_distribution.variance();
}