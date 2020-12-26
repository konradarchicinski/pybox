#include <iostream>
#include <chrono>
#include <random>

using namespace std;

int seed()
{
    int seed_number = ((mt19937::result_type)
                           chrono::duration_cast<chrono::seconds>(
                               chrono::system_clock::now().time_since_epoch())
                               .count() +
                       (mt19937::result_type)
                           chrono::duration_cast<chrono::microseconds>(
                               chrono::high_resolution_clock::now().time_since_epoch())
                               .count());
    random_device _random_device;
    return _random_device() ^ seed_number;
}

template <typename distribution_type>
vector<float> generate_numbers(distribution_type distribution, int data_lenght)
{
    mt19937 generator(seed());

    vector<float> data(data_lenght);
    for (size_t i = 0; i < data.size(); ++i)
    {
        data[i] = distribution(generator);
    }

    return data;
}

vector<float> from_normal_distribution(float mean, float std, int data_lenght)
{
    std::normal_distribution<float> normal_distribution(mean, std);
    return generate_numbers<std::normal_distribution<float>>(
        normal_distribution, data_lenght);
}

vector<float> from_student_t_distribution(float nu, int data_lenght)
{
    std::student_t_distribution<float> t_distribution(nu);
    return generate_numbers<std::student_t_distribution<float>>(
        t_distribution, data_lenght);
}