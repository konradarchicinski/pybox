#include "externals/src/generators/mersenne_twister.h"

MersenneTwister::MersenneTwister(double lower_bound,
                                 double upper_bound,
                                 int long seed) : generator(seed),
                                                  uniform(lower_bound, upper_bound) {}
MersenneTwister::~MersenneTwister() {}

double MersenneTwister::random_uniform() { return uniform(generator); }
