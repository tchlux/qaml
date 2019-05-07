from rand import random_range
from exceptions import UsageError, AmbiguousTerm

# Return a boolean "is_numeric"
def is_numeric(obj):
    try:
        abs((.3*obj + 1*obj) - .3*obj)
        return True
    except: return False

# Get the number of bits by looking at the assigned coefficients.
def get_num_bits(coefs):
    num_bits = 0
    for name in coefs:
        if (name[0] == "a"):
            num_bits = max(num_bits, int(name[1:]))
        elif (name[0] == "b"):
            nums = name[1:].split("b")
            for num in nums: num_bits = max(num_bits, int(num))
        elif (name[0] == "p"):
            num_bits = max(num_bits, int(name[1:]))
        elif (name[0] == "c"):
            num_bits = max(num_bits, 1)
        else:
            raise(UsageError(f"Unrecognized coefficient '{name}'."))
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
class ExhaustiveSearch():
    # Initialize this ExhaustiveSearch with the provided coefficients.
    def __init__(self, coeficients, constant=0):
        self.coeficients = coeficients.copy()
        self.num_bits = max(map(max, coeficients)) + 1
        self.constant = constant

    # Generate samples from the system, yield bits and energy.
    def samples(self, num_samples=1000):
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
# more readable interface for QBSolv, the built-in simulator.
class QBSolveAnnealer(ExhaustiveSearch):
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


# When this annealer is used, the program is actually run on the real
# hardware. The results are returned.
class QuantumAnnealer(ExhaustiveSearch):
    # Do the pecuiliar steps necessary to generate samples from QBSolv.
    def samples(self, num_samples=20):
        from dwave.system.samplers import DWaveSampler
        from dwave.system.composites import EmbeddingComposite
        # Construct a sampler over a real quantum annealer.
        from setup import token
        sampler = DWaveSampler(token=token)
        # Use an automatic embedding over the machine.
        response = EmbeddingComposite(sampler).sample_qubo(
            self.coeficients, num_reads=num_samples)
        for out in response.data():
            # Get the output from the data.
            bits = tuple(out.sample[b] for b in sorted(out.sample))
            energy = out.energy
            count = out.num_occurrences
            # Check to see what the percentage of chains that are broken in this solution.
            break_frac = 100*out.chain_break_fraction
            if break_frac > 0: print(f"WARNING ({__file__}): {break_frac:.2f}% of chains broken.")
            # Yield all of the outputs (based on their occurrence).
            for i in range(count): yield bits, energy + self.constant

# A class for holding QUBO objects that supports "addition".
class QUBO(dict):
    def __init__(self, *args, **kwargs):
        # Handle the creation of a QUBO from another dictionary.
        if len(args) > 0:
            other_dict, args = args[0], args[1:]
            for k in other_dict: self[k] = other_dict[k]
        # Copy in any keyword arguments.
        if len(kwargs) > 0:
            for k in kwargs: self[k] = kwargs[k]
        return super().__init__(*args)

    # Verify that this QUBO equals another term-for-term.
    def __eq__(self, other):
        for term in self:
            if (other.get(term,0) != self.get(term,0)):
                print(term, other.get(term,0), self.get(term,0))
                return False
        for term in other:
            if (other.get(term,0) != self.get(term,0)):
                print(term, other.get(term,0), self.get(term,0))
                return False
        return True

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

    # Retrieve an item from this QUBO.
    def __getitem__(self, key, *args, **kwargs):
        # Retrieve based on string access (in 1-indexed mathematical form).
        if type(key) == str:
            if (key[0] == 'b') and (key.count('b') == 1):
                i1, i2 = map(int, key[1:])
                i1, i2 = min(i1,i2), max(i1,i2)
                key = f"b{i1}b{i2}"
            elif (key.count('b') == 2):
                i1, i2 = map(int, key[1:].split('b'))
                i1, i2 = min(i1,i2), max(i1,i2)
                key = f"b{i1}b{i2}"
            return super().__getitem__(key, *args, **kwargs)
        # Retrieve based on tuple access (in 0-indexed integer form).
        elif type(key) == tuple:
            if (key[0] == key[1]):
                return super().__getitem__(f"a{key[0]+1}", *args, **kwargs)
            else:
                return super().__getitem__(f"b{key[0]+1}b{key[1]+1}", *args, **kwargs)

    # Make sure that items are set correctly into this qubo.
    def __setitem__(self, key, value, *args, **kwargs):
        if (len(key) == 0): raise(UsageError("QUBO keys must be 'a', 'b', or 'c' type."))
        if (not is_numeric(value)):
            raise(UsageError(f"Expected a numeric value, received {type(value)} instead."))
        if (key[0] == 'a'):
            return super().__setitem__(key, value, *args, **kwargs)
        elif (key[0] == 'b'):
            if (key.count('b') == 1):
                if (len(key) != 3): raise(AmbiguousTerm(f"Interaction term '{key}' is unclear, for >1 digit numbers use 'b#b#' specification."))
                i1, i2 = map(int, key[1:])
                i1, i2 = min(i1,i2), max(i1,i2)
                return super().__setitem__(f"b{i1}b{i2}", value, *args, **kwargs)
            elif (key.count('b') == 2):
                i1, i2 = map(int, key[1:].split('b'))
                i1, i2 = min(i1,i2), max(i1,i2)
                return super().__setitem__(f"b{i1}b{i2}", value, *args, **kwargs)
            else: raise UsageError(f"Provided term '{key}' has too many b's.")
        elif (key[0] == 'c'): super().__setitem__(key, value, *args, **kwargs)
        elif (len(key) == 2) and (type(key) == tuple) and all(type(v) == int for v in key):
            if key[0] == key[1]:
                return super().__setitem__(f"a{key[0]}", value, *args, **kwargs)
            i1, i2 = min(key), max(key)
            return super().__setitem__(f"b{i1+1}b{i2+1}", vaalue, *args, **kwargs)
        else: raise(UsageError(f"Unexpected key '{key}'."))

    # Make a pretty printout of this QUBO.
    def __str__(self, log=False):
        import math
        key_to_bit = lambda k: (int(k[1:]) if k[0] == 'a' else
                                max(map(int,k[1:].split('b'))) 
                                if k[0] == 'b' else 1)
        if len(self) > 0:
            bits = max(map(key_to_bit, self))
        else:
            return "This QUBO has no defined bits."
        # Keep track of the column widths.
        col_widths = [0] * bits
        rows = []
        for i in range(bits):
            row = []
            for j in range(0,i):
                v = self.get(f'b{j+1}b{i+1}', 0)
                if (v != 0) and log: v = int(round(math.log(abs(v),2))) * (-1 if v < 0 else 1)
                if (type(v) == int): row.append( str(v) )
                else:                row.append( f"{v: .2f}" )
            v = self.get(f'a{i+1}', 0)
            if (v != 0) and log: v = int(round(math.log(v,2))) * (-1 if v < 0 else 1)
            if (type(v) == int): row.append( str(v) )
            else:                row.append( f"{v: .2f}" )
            rows.append( row )
            # Update the column widths.
            for i,v in enumerate(row): col_widths[i] = max(len(v), col_widths[i])

        for i in range(len(rows)):
            rows[i] = "  " + "  ".join([f"{v:^{width}s}" for (v,width) in zip(rows[i], col_widths)])

        max_width = max(map(len, rows))
        return ' ' + super().__str__() + '\n ' + '-'*max_width + "\n" + "\n".join(rows) + '\n ' + '-'*max_width

        

# Given some of the coefficients, generate dictionary with all
# coeficients ready to be provided to a quantum annealer in the form
# { (#, #) : value }, where "#" are nonnegative integers and "value"
# are floating point numbers.
def make_qubo(display=False, **coefs):
    from itertools import combinations
    # Convert shorthand interaction coefficients to full form.
    for c in [c for c in coefs if c[0] == "b"]:
        if c.count("b") == 1:
            if len(c) == 3:
                c1, c2 = map(int,c[1:])
                coefs[f"b{min(c1,c2)}b{max(c1,c2)}"] = coefs.pop(c)
            else:
                # Raise an exception for ambiguous usage.
                raise(AmbiguousTerm(f"Interaction term '{c}' is unclear, for >1 digit numbers use 'b#b#' specification."))
        else:
            # Make sure that the b-coefficients are in increasing order.
            c1, c2 = map(int,c.split('b')[1:])
            coefs[f"b{min(c1,c2)}b{max(c1,c2)}"] = coefs.pop(c)
    num_bits = get_num_bits(coefs)
    # Generate the linear coeficients.
    output_coefs = {}
    for b1 in range(num_bits):
        output_coefs[(b1,b1)] = coefs.get(f"a{b1+1}",0)
    # Generate the quadratic coefficients.
    for (b1,b2) in combinations(range(num_bits),2):
        output_coefs[(b1,b2)] = coefs.get(f"b{b1+1}b{b2+1}",0)
    # Return the full set of linear and quadratic coeficients.
    return output_coefs

# A convenience wrapper for executing a QUBO on a quantum annealer.
# 
# INPUT:
# 
#   num_samples    -- int, how many samples should be drawn. Default
#                     value is 2**(number of bits in system).
#   build_q_system -- A callable object that is provided a full QUBO
#                     and has a "samples" function to generate samples
#                     from the quantum annealing platform. Examples:
#                      ExhaustiveSearch, QBSolveAnnealer, QuantumAnnealer
#   min_only       -- True if only the states with minimum observed
#                     energy should be reported. False to show all states.
#   display        -- True if outputs should be printed to user as table.
#   **coefs        -- Dictionary of coeficients in the form
#                      { a# : value ... b#b# : value ... c : value },
#                     where "#" are natural numbers and "c" is optional.
# 
# OUTPUT:
# 
#    A tuple of tuple of observed states sorted by energy first, then
#    bit pattern second.
# 
def run_qubo(num_samples=None, build_q_system=ExhaustiveSearch,
             min_only=True, display=True, rounded=5, **coefs):
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
    if display: print(f"Running {num_samples} times with:\n{QUBO(coefs)}")
    # Execute the samples on the system.
    for (bits, energy) in system.samples(num_samples):
        if rounded: energy = round(energy, rounded)
        if (energy == 0): energy = abs(energy)
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

    # Convert results to only be the sorted set of bits.
    return [list(b) for (e,b) in sorted(results)]
