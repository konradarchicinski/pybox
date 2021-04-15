#include "extern/src/maths/special_functions.h"
#include "extern/src/distributions/exponential_distribution.h"

ExponentialDistribution::ExponentialDistribution(double _lambda)
{
    left_support = 0.0;

    lambda = _lambda;
}

double ExponentialDistribution::pdf(const double &x) const
{
    return lambda * exp(-lambda * x);
}
double ExponentialDistribution::cdf(const double &x) const
{
    return 1 - exp(-lambda * x);
}
double ExponentialDistribution::ppf(const double &q) const
{
    return -log(1 - q) / lambda;
}

double ExponentialDistribution::mean() const
{
    return 1.0 / lambda;
}
double ExponentialDistribution::variance() const
{
    return 1 / (lambda * lambda);
}
