// cppimport
#include "extern/pybind11/pybind11.h"
#include "extern/pybind11/stl.h"
#include "extern/src/maths/descriptive_statistics.h"
// #include <pybind11/pybind11.h>
// #include <pybind11/stl.h>
// #include "numbers_generator.hpp"

PYBIND11_PLUGIN(numbers_generator_wrap)
{
      pybind11::module m("numbers_generator_wrap",
                         "NumbersGenerator plugin written in C++.");
      m.def("from_normal_distribution",
            &from_normal_distribution,
            "Generate vector of numbers from normal distribution.");
      m.def("from_student_t_distribution",
            &from_student_t_distribution,
            "Generate vector of numbers from student-t distribution.");
      return m.ptr();
}

/*
<%
cfg['compiler_args'] = ['-std=c++11']
cfg['sources'] = ['numbers_generator.cpp']
setup_pybind11(cfg)
%>
*/