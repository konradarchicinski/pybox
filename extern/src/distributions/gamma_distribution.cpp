#include "extern/src/maths/special_functions.h"
#include "extern/src/distributions/gamma_distribution.h"

GammaDistribution::GammaDistribution(double _k, double _theta)
{
    left_support = 0.0;

    k = _k;
    theta = _theta;
}

double GammaDistribution::pdf(const double &x) const
{
    return pow(x, k - 1) * exp(-x / theta) / (tgamma(k) * pow(theta, k));
}
double GammaDistribution::cdf(const double &x) const
{
    return gammainc(k, x / theta) / tgamma(k);
}

double GammaDistribution::mean() const
{
    return k * theta;
}
double GammaDistribution::variance() const
{
    return k * theta * theta;
}
