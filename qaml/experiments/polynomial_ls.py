
# Set and print the experimental configuration information.
simulated = True
sample_func = lambda n: 500 * n
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
    print(f"Automatically redirecting output to '{stdout_name}'..")
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

# Display a header.
for bits in range(2, 7+1):
    print('_'*70)
    print("bits: ",bits)
    # Construct the circuit.
    circuit = Circuit()
    a = circuit.Number(bits=bits, exponent=-bits, signed=False)
    b = circuit.Number(bits=bits, exponent=-bits, signed=False)
    circuit.add( a*b - 1 )
    circuit.add( a**2 + b**2 - 1 )
    circuit.add( a - b )
    # Run the experiment.
    circuit.run(min_only=False, num_samples=sample_func(bits),
                system=system, **run_kwargs)
    print(flush=True)
