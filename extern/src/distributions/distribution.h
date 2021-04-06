#ifndef DISTRIBUTION
#define DISTRIBUTION

#include <vector>
#include <cmath>

class Distribution
{
private:
    const double QUANTILE_TOLERANCE = 1e-15;
    const int ITERATIONS_LIMIT = 1e+4;

public:
    double left_support = -1.0 / 0.0;
    double right_support = 1.0 / 0.0;

    double location = 0.0;
    double scale = 1.0;

    virtual double pdf(double x) = 0;
    virtual double cdf(double x) = 0;
    virtual double ppf(double q);
    std::vector<double> simulate(long int simulations_number,
                                 long int seed = 1);

    virtual double mean() = 0;
    virtual double variance() = 0;
};

#endif
