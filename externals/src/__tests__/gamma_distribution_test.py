#!/usr/bin/env python
from pybox.tests import PyBoxTest

test = PyBoxTest.register(test_type='C++')
test.create(
    test_file='externals/src/__tests__/gamma_distribution_test.cc',
    source_files=['externals/src/distributions/distribution.cc',
                  'externals/src/distributions/gamma_distribution.cc',
                  'externals/src/maths/special_functions.cc',
                  'externals/src/generators/mersenne_twister.cc'])
test.run
