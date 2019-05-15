from qaml.discover.solve_truth_table import find_qubo, find_int_qubo
from qaml.discover.construct_truth_table import int_add_table
from qaml.qubo import run_qubo, QUBO

# Find the QUBO that correctly implements unsigned 2-bit integer addition.
# Find both the real-valued and integer-valued results and print.

# Generate the truth table for 2-bit unsigned integer addition.
b = 2
tt = int_add_table(n_bits=b)
print("Searching for a QUBO for the following truth table:")
print()
for row in tt: print("",row)
print()

# Initialize QUBO object to receive output.
qubo = QUBO(a1=4**(b-1))
# Enforce an energy gap of one between ground and first excited state.
gap = 0.0
# Begin.
print()
print("Finding feasible solution..")
# First find a real-valued solution to the problem.
q = find_qubo(tt, random=False, gap=gap, qubo=qubo)
print(q)
print("Verifying solution..")
sol = run_qubo(q, display=False)
if sol == tt:
    tt = sol
    print('-'*70)
    print("Using the following truth table to find integer solution:")
    for i,row in enumerate(tt): print("", row)
    # Find the integer form of the QUBO next, using the truth table solution.
    q = find_int_qubo(tt, gap=gap, display=False, qubo=qubo)
    # Check to make sure that the outputs are correct.
    out = run_qubo(q, display=False)
    if out == tt:
        print()
        print("Successfully found working integer QUBO!")
        print()
        # Print out the full table to the user.
        run_qubo(q)
else:
    print("Failed to match..")
    exit()
    sol = run_qubo(q, min_only=False)
