#ifndef SPECIAL_FUNCTIONS_H
#define SPECIAL_FUNCTIONS_H

#define _USE_MATH_DEFINES

#include <cmath>
#include <cfloat>

double erfinv(double y);
double betainc(double a, double b, double x);
double gammainc(double a, double x);

#endif