
# Set and print the experimental configuration information.
simulated = True
sample_func = lambda num_bits: 500 * num_bits
print_to_file = not simulated
run_kwargs = dict(and_strength=1/8, chain_strength=1)

# Setup the "system" for evaluating the QUBOs.
from qaml import QuantumAnnealer, ExhaustiveSearch, QBSolve
if simulated: system = ExhaustiveSearch
else:         system = QuantumAnnealer

# Remove the "chain_strength" argument for simulated results.
if simulated: run_kwargs.pop("chain_strength")

import time
if print_to_file:
    # Set the "print" location to be a file.
    import os, sys
    stdout_name = f"{'sim' if simulated else 'real'}_{os.path.basename(__file__)[:-3]}_results.txt"
    # stderr_name = f"{'sim' if simulated else 'real'}_{os.path.basename(__file__)[:-3]}_errors.txt"
    sys.stdout = open(stdout_name, 'a')
    # sys.stderr = open(stderr_name, 'a')

# Print out a description of the experimental setup.
print()
print('='*70)
print()
print(time.ctime())
print()

from qaml import Circuit
from qaml.discover.solve_truth_table import primes_up_to

for bits in range(2, 8+1):
    # Pick the prime numbers to construct a biprime.
    options = primes_up_to(2**bits)
    num1, num2 = options[-2:]
    # Display a header.
    print()
    print('-'*70)
    print("bits: ",bits, flush=True)
    print(f"{num1} x {num2} = {num1 * num2}", flush=True)
    # Construct the circuit.
    circuit = Circuit()
    a = circuit.Number(bits=bits, exponent=0, signed=False)
    b = circuit.Number(bits=bits, exponent=0, signed=False)
    circuit.add( a*b - (num1*num2) )
    # Run the experiment.
    circuit.run(min_only=False, num_samples=sample_func(bits),
                system=system, **run_kwargs)
    print(flush=True)
