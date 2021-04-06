#ifndef SPECIAL_FUNCTIONS
#define SPECIAL_FUNCTIONS

#define _USE_MATH_DEFINES

#include <cmath>
#include <cfloat>

double erfinv(double y);
double betainc(double a, double b, double x);
double gammainc(double a, double x);

#endif