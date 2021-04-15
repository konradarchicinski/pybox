#!/usr/bin/env python
from pybox.tests import PyBoxTest

test = PyBoxTest.register(test_type='C++')
test.create(test_file='extern/src/__tests__/exponential_distribution_test.cpp',
            source_files=[
                'extern/src/distributions/distribution.cpp',
                'extern/src/distributions/exponential_distribution.cpp',
                'extern/src/maths/special_functions.cpp',
                'extern/src/generators/mersenne_twister.cpp'
            ])
test.run
