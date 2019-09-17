
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

import random
# Seed the random number generator for consistency.
random.seed(0)
random_range = (-4, 4)
random_divisor = 4
number = dict(
    bits = 4,
    exponent = -3,
    signed = True
)

# Display a header.
for complexity in range(2, 8+1):
    print('_'*70)
    print("complexity: ",complexity)
    # Construct the circuit.
    circuit = Circuit()
    # Create the variables.
    variables = []
    for i in range(complexity):
        variables.append( circuit.Number(**number) )
    # Create the linear equations over those variables.
    for eq in range(complexity):
        multipliers = [random.randint(*random_range) / random_divisor
                       for i in range(len(variables))]
        equation = multipliers[0] * variables[0]
        for i in range(1,len(variables)):
            equation += multipliers[i] *  variables[i]
        circuit.add( equation )
    # Run the experiment.
    circuit.run(min_only=False, num_samples=sample_func(complexity),
                system=system, display=True, **run_kwargs)
    print(flush=True)

    
