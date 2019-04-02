from exceptions import UsageError, AmbiguousTerm

# Get the number of bits by looking at the assigned coefficients.
def get_num_bits(coefs):
    num_bits = 0
    for name in coefs:
        for char in name:
            try: num_bits = max(num_bits, int(char))
            except: pass
    return num_bits

# Given an integer, convert it into a binary bit representation.
def number_to_bits(number, num_bits=None):
    # Compute the required number of bits if that is not provided.
    if num_bits == None:
        import math
        if number <= 1: num_bits = 1
        else:           num_bits = 1 + int(math.log(number, 2))
    # Compute the binary representation starting with most significant bit.
    bits = [0] * num_bits
    for i in range(num_bits):
        value = 2 ** (num_bits-i-1)
        bits[i] = int(number // value > 0)
        if bits[i]: number -= value
    return tuple(bits)

# This is a simple brute force quantum annealer base class, designed
# to be subclassed by more advanced techniques.
class QuantumAnnealer():
    # Initialize this QuantumAnnealer with the provided coefficients.
    def __init__(self, coeficients, constant=0):
        self.coeficients = coeficients.copy()
        self.num_bits = max(map(max, coeficients)) + 1
        self.constant = constant

    # Generate samples from the system, yield bits and energy.
    def samples(self, num_samples=1000):
        from util.random import random_range
        for number in random_range(2**self.num_bits, count=num_samples):
            bits = number_to_bits(number, self.num_bits)
            yield (bits, self.energy(bits))

    # Given a set of bits, compute the energy of that set of bits and return it.
    def energy(self, bits):
        if (len(bits) != self.num_bits):
            raise(UsageError(f"Expected {self.num_bits}, but received {len(bits)}."))
        energy = 0.0
        for (i1, i2) in self.coeficients:
            if (bits[i1] and bits[i2]):
                energy += self.coeficients[(i1,i2)]
        return energy + self.constant

# A wrapper for the crappy provided solver by QBSolv, this defines a
# more readable interface for QBSolv, the built-in simulator. Run with:
# 
#   source ../quantum/bin/activate && python hw_2.py
# 
class QBSolveAnnealer(QuantumAnnealer):
    # Do the pecuiliar steps necessary to generate samples from QBSolv.
    def samples(self, num_samples=20):
        from dwave_qbsolv import QBSolv
        for i in range(num_samples):
            system = QBSolv().sample_qubo(self.coeficients)
            for output in system.samples(1): pass
            bits = tuple(output[b] for b in sorted(output))
            energy = system.data_vectors["energy"][0]
            if (energy == 0): energy = abs(energy)
            yield (bits, energy + self.constant)


# A class for holding QUBO objects that supports "addition".
class QUBO(dict):
    # Define a copy operator that generates a new QUBO.
    def copy(self): return QUBO(super().copy())

    # Define a new add operator.
    def __add__(self, other):
        # Initialize a dictionary with all values from both.
        output = other.copy()
        output.update(self)
        # Add the intersections of the two together.
        for k in set(other).intersection(set(self)):
            output[k] = output[k] + other[k]
        # Return the new QUBO.
        return output

    # "radd" is the same as the add operation.
    def __radd__(*args, **kwargs): return self.__add__(*args, **kwargs)

# Given some of the coefficients, generate dictionary with all
# coeficients ready to be provided to a quantum annealer.
def make_qubo(display=False, **coefs):
    from itertools import combinations
    num_bits = get_num_bits(coefs)
    # Convert shorthand interaction coefficients to full form.
    for c in [c for c in coefs if c[0] == "b"]:
        if c.count("b") == 1:
            if len(c) == 3:
                coefs[f"b{c[1]}b{c[2]}"] = coefs.pop(c)
            else:
                # Raise an exception for ambiguous usage.
                raise(AmbiguousTerm("Interaction term '{c}' is unclear, for >1 digit numbers use 'b#b#' specification."))
    # Generate the linear coeficients.
    output_coefs = {}
    for b1 in range(num_bits):
        output_coefs[(b1,b1)] = coefs.get(f"a{b1+1}",0)
    # Generate the quadratic coefficients.
    for (b1,b2) in combinations(range(num_bits),2):
        output_coefs[(b1,b2)] = coefs.get(f"b{b1+1}b{b2+1}",0)
    # Return the full set of linear and quadratic coeficients.
    return output_coefs

# Given the coefficients, use the QBSolv library to simulate the
# execution of the following code on a quantum computer.
def run_qubo(num_samples=None, build_q_system=QuantumAnnealer,
             min_only=True, display=True, **coefs):
    if len(coefs) == 0:
        raise(UsageError("Missing QUBO coefficients!"))
    # Allow for the pinning of bits.
    pinning = False
    pin_ones = 0
    if any((c[0] == "p") for c in coefs):
        num_bits = get_num_bits(coefs)
        coefs[f"a{num_bits+1}"] = -1
        for c in [c for c in coefs if c[0] == "p"]:
            value = coefs.pop(c)
            pinning = True
            pin_ones += int(value == 1)
            coefs[f"b{c[1:]}b{num_bits+1}"] = (-1) ** value

    # Generate the full set of coefficients for this problem.
    all_coefs = make_qubo(**coefs)
    # Take samples by calling the simulator repeatedly, track results.
    results = {}
    system = build_q_system(all_coefs, constant=coefs.get('c',0))
    # If the number of samples is not provided, try enough for all combinations.
    if num_samples == None: num_samples = 2 ** system.num_bits
    print(f"Running {num_samples} times with coeficients:\n  {all_coefs}\n")
    # Execute the samples on the system.
    for (bits, energy) in system.samples(num_samples):
        # Hide the "pin" bit effects if it was used.
        if pinning:
            bits = bits[:-1]
            energy += int(pinning) + pin_ones
        # Update the record of energy and output.
        count = results.get((energy, bits), 0)
        # Store the results.
        results[(energy, bits)] = count + 1

    # If the user only wants to see minimum energy solutoins, get rid of others.
    if min_only:
        min_energy = min(results, key=lambda k: k[0])[0]
        for (e,b) in list(results):
            if (e > min_energy): results.pop((e,b))
        
    if display:
        # Print out the results in a neat format, sorted by energy then bit pattern.
        b_space = 3
        for r in results: b_space = max(b_space,len(str(r)))
        print(f" {'Bits':<{b_space}s}\tOccurrence\tEnergy")
        for (energy, bits) in sorted(results):
            occurence = results[(energy, bits)]
            print(f" {str(bits):<{b_space}s}\t {occurence}\t\t {energy}")
        print()

    # Convert results to only be the sorted set of bits
    return tuple(b for (e,b) in sorted(results))

