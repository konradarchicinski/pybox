#ifndef DISTRIBUTION_H
#define DISTRIBUTION_H

#include <cmath>
#include <vector>

class Distribution
{
public:
    Distribution(){};
    virtual ~Distribution(){};

    double left_support = -1.0 / 0.0;
    double right_support = 1.0 / 0.0;

    double location = 0.0;
    double scale = 1.0;

    virtual double pdf(const double &x) const = 0;
    virtual double cdf(const double &x) const = 0;
    virtual double ppf(const double &q) const;
    std::vector<double> simulate(
        const long int &simulations_number,
        const int &seed = 1);

    virtual double mean() const = 0;
    virtual double variance() const = 0;

private:
    const double QUANTILE_TOLERANCE = 1e-15;
    const int ITERATIONS_LIMIT = 1e+4;
};

#endif
