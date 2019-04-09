


from integer import *
MODIFY_TWO_BIT_ADD = True
if MODIFY_TWO_BIT_ADD:
    print("Modified 2-bit error cases:")
    print()
    two_bit = int_add(*range(1,2*3+1+1))
    two_bit["b12"] = 0
    two_bit["b23"] = 0
    two_bit["b34"] = 0
    two_bit["b45"] = 0
    two_bit["b14"] = 0
    two_bit["b25"] = 0
    two_bit["b17"] = 0
    two_bit["b37"] = 0
    two_bit["b57"] = 0

    truth = run_qubo(**int_add_two, display=False)
    from qubo import QuantumAnnealer, make_qubo
    system = QuantumAnnealer(make_qubo(**two_bit))
    outputs = run_qubo(**two_bit, min_only=False)
    bad = []
    for row in outputs:
        energy = system.energy(row)
        if (energy == 0) and (row not in truth):
            bad.append((row, energy, "invalid solution"))
        elif (energy > 0) and (row in truth):
            bad.append((row, energy, "should be valid"))
        elif (energy < 0) and (row not in truth):
            bad.append((row, energy, "should not be valid"))
        elif (energy < 0) and (row in truth):
            bad.append((row, energy, "should be valid, but 0"))

    bad = sorted(bad)
    bad.sort(key = lambda i: i[1])
    bad.sort(key = lambda i: i[2])
    for row, energy, details in bad:
        print(tuple(row), f"{energy: 2.1f}", "", details)



    # from adder import two_int_adder_4n
    # run_qubo(**two_int_adder_4n
