#include "externals/src/maths/special_functions.h"

#define MAXDOUBLE DBL_MAX
#define CENTRAL_RANGE 0.7

double erfinv(double y)
{
    // Function to calculate inverse error function. Rational approximation
    // is used to generate an initial approximation, which is then improved
    // to full accuracy by two steps of Newton's method.  Code is a direct
    // translation of the erfinv m file in matlab version 2.0.
    // Author:  Gary L. Pavlis, Indiana University
    // Date:  February 1996
    double x, z, num, dem;

    // coefficients in rational expansion
    double a[4] = {0.886226899, -1.645349621, 0.914624893, -0.140543331};
    double b[4] = {-2.118377725, 1.442710462, -0.329097515, 0.012229801};
    double c[4] = {-1.970840454, -1.624906493, 3.429567803, 1.641345311};
    double d[2] = {3.543889200, 1.637067800};

    if (fabs(y) > 1.0)
        return atof("NaN");
    if (fabs(y) == 1.0)
        return copysign(1.0, y) * MAXDOUBLE;

    if (fabs(y) <= CENTRAL_RANGE)
    {
        z = y * y;
        num = ((a[3] * z + a[2]) * z + a[1]) * z + a[0];
        dem = (((b[3] * z + b[2]) * z + b[1]) * z + b[0]) * z + 1.0;
        x = y * num / dem;
    }
    else if ((fabs(y) > CENTRAL_RANGE) && (fabs(y) < 1.0))
    {
        z = sqrt(-log((1.0 - fabs(y)) / 2.0));
        num = ((c[3] * z + c[2]) * z + c[1]) * z + c[0];
        dem = (d[1] * z + d[0]) * z + 1.0;
        x = copysign(1.0, y) * num / dem;
    }

    //Two steps of Newton-Raphson correction
    x = x - (erf(x) - y) / ((2.0 / sqrt(M_PI)) * exp(-x * x));
    x = x - (erf(x) - y) / ((2.0 / sqrt(M_PI)) * exp(-x * x));

    return x;
}

#define STOP 1.0e-8
#define TINY 1.0e-30

double betainc(double a, double b, double x)
{
    // https://codeplea.com/incomplete-beta-function-c

    if (x < 0.0 || x > 1.0)
        return 1.0 / 0.0;

    // The continued fraction converges nicely for x < (a+1)/(a+b+2)
    // Use the fact that beta is symmetrical.
    if (x > (a + 1.0) / (a + b + 2.0))
        return (1.0 - betainc(b, a, 1.0 - x));

    // Find the first part before the continued fraction.
    const double lbeta_ab = lgamma(a) + lgamma(b) - lgamma(a + b);
    const double front = exp(log(x) * a + log(1.0 - x) * b - lbeta_ab) / a;

    // Use Lentz's algorithm to evaluate the continued fraction.
    double f = 1.0, c = 1.0, d = 0.0;

    int i, m;
    for (i = 0; i <= 200; ++i)
    {
        m = i / 2;

        double numerator;
        // First numerator is 1.0.
        if (i == 0)
            numerator = 1.0;
        // Even term.
        else if (i % 2 == 0)
            numerator = (m * (b - m) * x) / ((a + 2.0 * m - 1.0) * (a + 2.0 * m));
        // Odd term.
        else
            numerator = -((a + m) * (a + b + m) * x) / ((a + 2.0 * m) * (a + 2.0 * m + 1));

        // Do an iteration of Lentz's algorithm.
        d = 1.0 + numerator * d;
        if (fabs(d) < TINY)
            d = TINY;
        d = 1.0 / d;

        c = 1.0 + numerator / c;
        if (fabs(c) < TINY)
            c = TINY;

        const double cd = c * d;
        f *= cd;

        // Check for stop.
        if (fabs(1.0 - cd) < STOP)
            return front * (f - 1.0);
    }

    // Needed more loops, did not converge.
    return 1.0 / 0.0;
}

#define DOUBLE_LIMIT 1e-14

double gammainc(double s, double x)
{
    double initial_value = pow(x, s) * exp(-x);

    double rising_factorial = s;
    double term = pow(x, 0) / rising_factorial;

    int k = 0;
    double run_sum = term;
    while (term > DOUBLE_LIMIT)
    {
        k++;
        rising_factorial *= (s + k);

        term = pow(x, k) / rising_factorial;
        run_sum += term;
    }

    return initial_value * run_sum;
}
