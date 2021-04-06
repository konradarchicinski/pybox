#include <iostream>
#include <vector>
#include <fstream>
#include <iomanip>
#include <limits>

#include "extern/src/distributions/chi_square_distribution.h"

using namespace std;

int main()
{
    ofstream output_file(
        "extern/src/__tests__/outputs/chi_square_distribution_simulations.csv");

    typedef numeric_limits<double> dbl;
    output_file.precision(dbl::max_digits10);

    ChiSquareDistribution dist;

    cout << "Provide number of simulations: ";
    int n;
    cin >> n;

    vector<double> vc = dist.simulate(n);
    for (int i = 0; i < n; i++)
        output_file << vc[i] << "\n";
}
