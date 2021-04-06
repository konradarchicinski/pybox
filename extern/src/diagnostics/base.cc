#include "extern/src/diagnostics/base.h"
#include "extern/src/maths/descriptive_statistics.h"

double welch_test(std::vector<double> sample1, std::vector<double> sample2)
{
    int n1 = sample1.size();
    int n2 = sample2.size();
    double mean1 = mean(sample1);
    double mean2 = mean(sample2);
    double var1 = variance(sample1);
    double var2 = variance(sample2);

    double t_statistic = (mean1 - mean2) /
                         sqrt(var1 / n1 + var2 / n2);

    double degrees_of_freedom = pow(var1 / n1 + var2 / n2, 2) /
                                (pow(var1 / n1, 2) / (n1 - 1) +
                                 pow(var2 / n2, 2) / (n2 - 1));

    return t_statistic;
}