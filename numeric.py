from qubo import run_qubo
from logic import uint_min, int_min, abs_int

print("-"*70)
print("Numeric minimizer")
# run_qubo(a1=2**4, a2=2**3, a3=2**2, a4=2**1, a5=2**0, min_only=False)
bit_indices = list(range(1,4))
run_qubo(**(int_min(*bit_indices)), min_only=False)

exit()

# Run the half adder (the last bit is the carry bit)
print("-"*70)
print("Half Adder")
run_qubo(a1=1, a2=1, a3=1, a4=4,
         b12=2, b13=-2, b14=-4, b23=-2, b24=-4, b34=4)
print()


# # Positive two-bit addition.
# two_pos_add = [
#     (0,0, 0,0, 0,0),
#     (0, 0, 0, 1, 0, 1),
#     (0, 0, 1, 0, 1, 0),
#     (0, 0, 1, 1, 1, 1),
#     (0, 1, 0, 0, 0, 1),
#     (0, 1, 0, 1, 1, 0),
#     (0, 1, 1, 0, 1, 1),
#     (0, 1, 1, 1, 1, 1),
#     (1, 0, 0, 0, 1, 0),
#     (1, 0, 0, 1, 1, 1),
#     (1, 0, 1, 0, 1, 1),
#     (1, 0, 1, 1, 1, 1),
#     (1, 1, 1, 1, 1, 1),
# ]

# # Signed two-bit addition.
# two_sign_add = [
#     (0, 0, 0, 0, 0, 0),
#     (0, 0, 0, 1, 0, 1),
#     (0, 0, 1, 0, 0, 0),
#     (0, 0, 1, 1, 1, 1),
#     (0, 1, 0, 0, 0, 1),
#     (0, 1, 0, 1, 0, 1),
#     (0, 1, 1, 0, 0, 1),
#     (0, 1, 1, 1, 0, 0),
#     (1, 0, 0, 0, 0, 0),
#     (1, 0, 0, 1, 0, 1),
#     (1, 0, 1, 0, 0, 0),
#     (1, 0, 1, 1, 1, 1),
#     (1, 1, 1, 1, 1, 1),
# ]
