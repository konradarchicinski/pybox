#ifndef MERSENNE_TWISTER
#define MERSENNE_TWISTER

#include <random>
#include <chrono>

class MersenneTwister
{
private:
    std::mt19937 generator;
    std::uniform_real_distribution<double> uniform;

public:
    MersenneTwister(double lower_bound = 0.0,
                    double upper_bound = 1.0,
                    int long seed = std::chrono::system_clock::now()
                                        .time_since_epoch()
                                        .count());
    ~MersenneTwister();

    double random_uniform();
};

#endif