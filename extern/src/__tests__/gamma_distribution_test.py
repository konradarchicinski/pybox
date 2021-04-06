#!/usr/bin/env python
from pybox.tests import PyBoxTest

test = PyBoxTest.register(test_type='C++')
test.create(
    test_file='extern/src/__tests__/gamma_distribution_test.cc',
    source_files=['extern/src/distributions/distribution.cc',
                  'extern/src/distributions/gamma_distribution.cc',
                  'extern/src/maths/special_functions.cc',
                  'extern/src/generators/mersenne_twister.cc'])
test.run
