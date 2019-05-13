
# Set and print the experimental configuration information.
simulated = False
num_samples = lambda num_bits: 400 * num_bits
print_to_file = not simulated

import time
if print_to_file:
    # Set the "print" location to be a file.
    import os, sys
    stdout_name = f"{'sim' if simulated else 'real'}_{os.path.basename(__file__)[:-3]}_results.txt"
    stderr_name = f"{'sim' if simulated else 'real'}_{os.path.basename(__file__)[:-3]}_errors.txt"
    sys.stdout = open(stdout_name, 'a')
    sys.stderr = open(stderr_name, 'a')

# Print out a description of the experimental setup.
print()
print('='*70)
print()
print(time.ctime())
print()

# Define a convenience wrapper for calling "run_qubo" when collecting
# experimental data for addition and multiplication.
def run_experiment(qubo, samples, simulate=simulated):
    from qaml import run_qubo, QuantumAnnealer, ExhaustiveSearch
    # Pick the quantum system sampler based on "simulate".
    if simulate: system = ExhaustiveSearch
    else:        system = QuantumAnnealer
    # Run the experiment.
    run_qubo(**qubo, system=system, min_only=False, num_samples=samples)


from qaml import Circuit
from qaml.solve_truth_table import primes_up_to

for bits in range(2, 5+1):
    options = primes_up_to(2**bits)
    num1, num2 = options[-2:]
    print()
    print("bits: ",bits, flush=True)
    print(f"{num1} x {num2} = {num1 * num2}", flush=True)
    circuit = Circuit()
    a = circuit.Number(bits=bits, exponent=0, signed=False)
    b = circuit.Number(bits=bits, exponent=0, signed=False)
    circuit.add( a*b - (num1*num2) )
    qubo = circuit.assemble()
    # Run the experiment.
    run_experiment(qubo, num_samples(bits))

