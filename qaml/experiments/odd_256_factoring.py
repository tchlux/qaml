
# Set and print the experimental configuration information.
simulated = False
sample_func = lambda num_bits: 400 * num_bits
print_to_file = not simulated
run_kwargs = dict(and_strength=1/100, chain_strength=1/2)

# Using and strength 621002752  (1/4)        2173509632
#                    248401100  (1/10)       2359810457
#                     24840110  (1/100)      
#                      2484011  (1/1000)     2482769002
#                       248401  (1/10000)
#                        24840  (1/100000)

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

bits = 7
num1 = 491 # = 257 + 234
num2 = 509 # = 257 + 252
# Display a header.
print()
print('-'*70)
print("bits: ",bits, flush=True)
print(f"{num1} x {num2} = {num1 * num2}", flush=True)
# Construct the circuit.
circuit = Circuit()
p = circuit.Number(bits=bits, exponent=1, signed=False)
q = circuit.Number(bits=bits, exponent=1, signed=False)
circuit.add( (p + 257)*(q + 257) - (num1*num2) )
# Run the experiment.
circuit.run(min_only=False, num_samples=sample_func(bits),
            system=system, **run_kwargs)
print(flush=True)


