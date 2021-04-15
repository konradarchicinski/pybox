#ifndef STUDENT_T_DISTRIBUTION_H
#define STUDENT_T_DISTRIBUTION_H

#include <limits>
#include "extern/src/distributions/distribution.h"

class StudentTDistribution : public Distribution
{
public:
    StudentTDistribution(
        double _mu = 0.0, double _sigma = 1.0, double _nu = 4.0);
    virtual ~StudentTDistribution(){};

    double mu;
    double sigma;
    double nu;

    virtual double pdf(const double &x) const;
    virtual double cdf(const double &x) const;

    virtual double mean() const;
    virtual double variance() const;
};

#endif