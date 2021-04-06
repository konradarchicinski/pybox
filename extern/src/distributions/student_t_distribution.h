#ifndef STUDENT_T_DISTRIBUTION
#define STUDENT_T_DISTRIBUTION

#include <limits>
#include "extern/src/distributions/distribution.h"

class StudentTDistribution : public Distribution
{
public:
    double mu;
    double sigma;
    double nu;

    StudentTDistribution(
        double _mu = 0.0, double _sigma = 1.0, double _nu = 4.0)
    {
        mu = _mu;
        sigma = _sigma;
        nu = _nu;
    }
    ~StudentTDistribution(){};

    double pdf(double x);
    double cdf(double x);

    double mean();
    double variance();
};

#endif