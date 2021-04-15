#include "extern/src/maths/special_functions.h"
#include "extern/src/distributions/normal_distribution.h"

NormalDistribution::NormalDistribution(double _mu, double _sigma)
{
    mu = _mu;
    sigma = _sigma;
}

double NormalDistribution::pdf(const double &x) const
{
    return exp(-0.5 * (pow((x - mu) / sigma, 2))) /
           (sigma * sqrt(2 * M_PI));
}
double NormalDistribution::cdf(const double &x) const
{
    return 0.5 * (1 + erf((x - mu) / (sigma * sqrt(2))));
}
double NormalDistribution::ppf(const double &q) const
{
    return mu + sigma * sqrt(2) * erfinv(2 * q - 1);
}

double NormalDistribution::mean() const
{
    return mu;
}
double NormalDistribution::variance() const
{
    return sigma;
}
