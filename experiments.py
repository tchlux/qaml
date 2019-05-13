# Set and print the experimental configuration information.
simulated = True
num_bits = 3
block_size = 2
num_samples = 100 * num_bits
print_to_file = False

import time
if print_to_file:
    # Set the "print" location to be a file.
    import os, sys
    results_folder = "Addition_Results"
    stdout_name = f"{'sim' if simulated else 'real'}_{num_bits}-bit_{block_size}-block_{num_samples}-samples.txt"
    stderr_name = f"errors_{'sim' if simulated else 'real'}_{num_bits}-bit_{block_size}-block_{num_samples}-samples.txt"
    sys.stdout = open(os.path.join(results_folder, stdout_name), 'a')
    sys.stderr = open(os.path.join(results_folder, stderr_name), 'a')

# Print out a description of the experimental setup.
print()
print('='*70)
print()
print(time.ctime())
print()

# Define a convenience wrapper for calling "run_qubo" when collecting
# experimental data for addition and multiplication.
def run_experiment(qubo, simulate=simulated):
    from qubo import run_qubo, QuantumAnnealer, ExhaustiveSearch
    # Pick the quantum system sampler based on "simulate".
    if simulate: system = ExhaustiveSearch
    else:        system = QuantumAnnealer
    # Run the experiment.
    run_qubo(**qubo, system=system, min_only=False, num_samples=num_samples)

# Construct a half add QUBO
from integer import int_half_add
qubo = int_half_add(*list(range(1,3*num_bits + 2)))
print("Dense addition:")
print()
run_experiment(qubo)

if num_bits > 2:
    print()
    print('-'*70)
    print()
    # Construct a modular addition circuit.
    from math import ceil
    from integer import int_add_modular
    qubo = int_add_modular(num_bits, block_size, *list(range(1, 1 + 3*num_bits + ceil(num_bits/block_size))))
    print("Block addition:")
    print()
    run_experiment(qubo)
