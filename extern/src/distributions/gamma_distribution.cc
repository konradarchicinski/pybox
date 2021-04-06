#include "extern/src/distributions/gamma_distribution.h"
#include "extern/src/maths/special_functions.h"

double GammaDistribution::pdf(double x)
{
    return pow(x, k - 1) * exp(-x / theta) / (tgamma(k) * pow(theta, k));
}
double GammaDistribution::cdf(double x)
{
    return gammainc(k, x / theta) / tgamma(k);
}

double GammaDistribution::mean() { return k * theta; }
double GammaDistribution::variance() { return k * theta * theta; }
