#ifndef NUMBERS_GENERATOR_HPP
#define NUMBERS_GENERATOR_HPP

std::vector<float> from_normal_distribution(float mean, float std, int data_lenght);
std::vector<float> from_student_t_distribution(float nu, int data_lenght);

#endif