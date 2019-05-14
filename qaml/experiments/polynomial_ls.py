
# Set and print the experimental configuration information.
simulated = False
print_to_file = not simulated

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

# Define a convenience wrapper for calling "run_qubo" when collecting
# experimental data for addition and multiplication.
def run_experiment(qubo, samples, simulate=simulated):
    from qaml import run_qubo, QuantumAnnealer, ExhaustiveSearch, QBSolve
    # Pick the quantum system sampler based on "simulate".
    if simulate: system = QBSolve
    else:        system = QuantumAnnealer
    # Run the experiment.
    run_qubo(**qubo, system=system, min_only=False, num_samples=samples)


from qaml import Circuit

# for bits in range(2, 5+1):
bits = 4
print("bits: ",bits)
circuit = Circuit()
a = circuit.Number(bits=bits, exponent=-bits, signed=False)
b = circuit.Number(bits=bits, exponent=-bits, signed=False)
circuit.add( a*b - 1 )
circuit.add( a**2 + b**2 - 1 )
circuit.add( a - b )
qubo = circuit.assemble(and_rescale=5)
# Run the experiment.
run_experiment(qubo, 400*bits)

