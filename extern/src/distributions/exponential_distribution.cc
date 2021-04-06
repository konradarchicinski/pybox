#include "extern/src/distributions/exponential_distribution.h"
#include "extern/src/maths/special_functions.h"

double ExponentialDistribution::pdf(double x)
{
    return lambda * exp(-lambda * x);
}
double ExponentialDistribution::cdf(double x)
{
    return 1 - exp(-lambda * x);
}
double ExponentialDistribution::ppf(double q)
{
    return -log(1 - q) / lambda;
}

double ExponentialDistribution::mean() { return 1.0 / lambda; }
double ExponentialDistribution::variance() { return 1 / (lambda * lambda); }
