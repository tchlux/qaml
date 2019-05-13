
# # Construct a half add QUBO
# qubo = int_half_add(*list(range(1,3*num_bits + 2)))
# print("Dense addition:")
# print()
# run_experiment(qubo)

# if num_bits > 2:
#     print()
#     print('-'*70)
#     print()
#     # Construct a modular addition circuit.
#     from math import ceil
#     from integer import int_add_modular
#     qubo = int_add_modular(num_bits, block_size, *list(range(1, 1 + 3*num_bits + ceil(num_bits/block_size))))
#     print("Block addition:")
#     print()
#     run_experiment(qubo)
