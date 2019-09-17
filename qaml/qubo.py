import os
from qaml.systems import ExhaustiveSearch
from qaml.exceptions import UsageError, AmbiguousTerm

# A convenience wrapper for executing a QUBO on a quantum annealer.
# 
# INPUT:
# 
#   qubo        -- Dictionary of coeficients in the form
#                   { a# : value ... b#b# : value ... c : value },
#                  where "#" are natural numbers and "c" is optional.
#   num_samples -- int, how many samples should be drawn. Default
#                  value is 2**(number of bits in system).
#   system      -- A callable object that is provided a full QUBO
#                  and has a "samples" function to generate samples
#                  from the quantum annealing platform. Examples:
#                   ExhaustiveSearch, QBSolve, QuantumAnnealer
#   min_only    -- True if only the states with minimum observed
#                  energy should be reported. False to show all states.
#   display     -- True if outputs should be printed to user as table.
#   **system_kwargs -- The keyword arguments that should be passed
#                      to the system "sample" method. The most notable
#                      usage would be to pass "chain_strength=<float>"
#                      to decrease the frequency of chain breaks.
#                      The QuantumAnnealer System also has a 'verbose'
#                      option that could be turned off here.
# 
# OUTPUT:
# 
#    A list of lists of observed states sorted by energy first, then
#    bit pattern second. If "min_only" is True, then only the states
#    that obtained the minimum energy are returned.
# 
def run_qubo(qubo, num_samples=None, system=ExhaustiveSearch,
             min_only=True, display=True, rounded=5, **system_kwargs):
    # Make sure the provided QUBO is stored in "QUBO" class form.
    if (type(qubo) != QUBO): qubo = QUBO(qubo)
    # Take samples by calling the simulator repeatedly, track results.
    system = system(qubo, constant=qubo.get('c',0))
    # If the number of samples is not provided, try enough for all combinations.
    if num_samples == None: num_samples = min(2 ** system.num_bits, 1000)
    if display: print(f"Running {num_samples} times with:\n{qubo}")
    # Execute the samples on the system.
    results = {}
    for sample in system.samples(num_samples, **system_kwargs):
        # Get the bit pattern, pattern energy, and chain break fraction.
        bits, energy, cbf = sample
        if (type(cbf) != type(None)): cbf *= 100
        if rounded:       energy = round(energy, rounded)
        if (energy == 0): energy = abs(energy)
        count = results.get((energy, bits, cbf), 0)
        # Store the results.
        results[(energy, bits, cbf)] = count + sample.occurrence
    # If the user only wants to see minimum energy solutions, get rid of others.
    if min_only:
        min_energy = min(results, key=lambda k: k[0])[0]
        for (e,b,c) in list(results):
            if (e > min_energy): results.pop((e,b,c))
    # If all of the chain break fraction values are None, remove them.
    chain_breaks = True
    if all(c == None for (e,b,c) in results):
        chain_breaks = False
        results = {key[:-1]:results[key] for key in results}
    # If the user wants to display the outputs then print those.
    if display:
        cbf = "\tChain breaks" if chain_breaks else ""
        # Print out the results in a neat format, sorted by energy then bit pattern.
        b_space = 3
        for r in results: b_space = max(b_space,len(str(r[1])))
        o_space = 2
        for r in results: o_space = max(o_space, 1+len(str(results[r])))
        e_space = 4
        for r in results: e_space = max(e_space, 1+len(str(r[0])))
        print()
        print(f" {'Bits':<{b_space}s}\tOccurrence{cbf}\tEnergy")
        for sample in sorted(results):
            if (len(cbf) == 0):
                energy, bits = sample
                cbf_str = ""
            else:
                energy, bits, chain_breaks = sample
                cbf_str = f"{chain_breaks: 6.1f}%\t\t"
            occurrence = results[sample]
            print(f" {str(bits):<{b_space}s}\t{occurrence: {o_space}d}\t\t{cbf_str} {str(energy):>{e_space}s}")
        print()
    # Define a results class that contains the info about each result.
    class Results(list):
        # Old {  (energy, bits, chain break fraction) : (occurrence)  }
        info = {tuple(key[1]) : (key[0],) + key[2:] + (results[key],) for key in results}
        # New {  (bits) : (energy, chain break fraction, occurrence)  }
    # Convert results to only be the sorted set of bits.
    return Results(list(key[1]) for key in sorted(results))

# Given some of the coefficients, generate dictionary with all
# coeficients ready to be provided to a quantum annealer in the form
# { (#, #) : value }, where "#" are nonnegative integers and "value"
# are floating point numbers.
def make_dwave_qubo(display=False, **coefs):
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

# Given a QUBO object, get the rescale factor that will be used to fit
# the corresponding Ising model onto the physical hardware.  Assume
# that hardware allows "h" in range [-2,2] and "J" in range [-1,1].
def qubo_ising_rescale_factor(qubo):
    # If appropriate, convert QUBO into D-Wave format.
    if (type(qubo) == QUBO): qubo = make_dwave_qubo(**qubo)
    # Get the corresponding Ising model.
    h, J, _ = qubo_to_ising(qubo)
    # Get the max positive weight, divide 'h' values by 2 because
    # they are allowed a greater range on the hardware..
    rescale_factor = -float('inf')
    for coef in h: rescale_factor = max(abs(h[coef])/2, rescale_factor)
    for coef in J: rescale_factor = max(abs(J[coef]),   rescale_factor)
    # If no weight was assigned, or it is 0, then reset to 1.
    if (rescale_factor in {-float('inf'), 0}): max_weight = 1
    return rescale_factor

# Given a QUBO dictionary { (i,j):weight ... }, convert it to an Ising
# triple: ( { i:weight ... }, { (i,j):weight ... }, energy_offset )
def qubo_to_ising(Q):
    # If appropriate, convert QUBO into D-Wave format.
    if (type(Q) == QUBO): Q = make_dwave_qubo(**Q)
    # Create storage for outputs.
    h = {}
    J = {}
    offset = 0
    linear_offset = 0
    quadratic_offset = 0
    for (u, v), bias in Q.items():
        if u == v:
            h[u] = h.get(u, 0) + bias / 2
            linear_offset += bias
        else:
            if (bias != 0): J[(u, v)] = bias / 4
            h[u] = h.get(u, 0) + bias / 4
            h[v] = h.get(v, 0) + bias / 4
            quadratic_offset += bias
    offset += linear_offset / 2 + quadratic_offset / 4
    return h, J, offset

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

# Get the number of bits by looking at the assigned coefficients.
def get_num_bits(coefs):
    num_bits = 0
    for name in coefs:
        if (name[0] == "a"):
            num_bits = max(num_bits, int(name[1:]))
        elif (name[0] == "b"):
            nums = name[1:].split("b")
            for num in nums: num_bits = max(num_bits, int(num))
        elif (name[0] == "c"):
            num_bits = max(num_bits, 1)
        else:
            raise(UsageError(f"Unrecognized coefficient '{name}'."))
    return num_bits

# Return a boolean "is_numeric"
def is_numeric(obj):
    try:
        abs((.3*obj + 1*obj) - .3*obj)
        return True
    except: return False

# --------------------------------------------------------------------
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

    # Define a "contains" method that works with integers as well as strings.
    def __contains__(self, key):
        if (type(key) == int):
            return super().__contains__(f"a{key+1}")
        elif (type(key) == tuple):
            c1, c2 = min(key), max(key)
            return super().__contains__(f"b{c1+1}b{c2+1}")
        elif (type(key) == str):
            return super().__contains__(key)
        else:
            raise(TypeError(f"Unexpected key type {type(key)}, '{key}'."))

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

    # Define 'multiply' for ints and floats.
    def __mul__(self, num):
        if (type(num) not in {int, float}): raise(TypeError(f"QUBO only supports multiplication by {int} and {float}."))
        else: return QUBO({c:self[c]*num for c in self})
    # Define right hand multiply to be the same.
    def __rmul__(self, num): return self * num

    # Define 'divide' for ints and floats.
    def __truediv__(self, num):
        if (type(num) not in {int, float}): raise(TypeError(f"QUBO only supports division by {int} and {float}."))
        else: return QUBO({c:self[c]/num for c in self})

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
        # Retreive based on a single integer.
        elif type(key) == int:
            return super().__getitem__(f"a{key+1}", *args, **kwargs)

    # Make sure that items are set correctly into this qubo.
    def __setitem__(self, key, value, *args, **kwargs):
        # Handle standard 'a' terms.
        if (type(key) == int): return super().__setitem__(f"a{key+1}", value, *args, **kwargs)
        # Check for string keys.
        if (len(key) == 0): raise(UsageError("QUBO keys must be 'a', 'b', 'c', or 'p' type."))
        if (not is_numeric(value)):
            raise(UsageError(f"Expected a numeric value, received {type(value)} instead."))
        # Handle standard 'a' terms.
        if (key[0] == 'a'): return super().__setitem__(key, value, *args, **kwargs)
        # Handle interaction 'b' terms.
        if (key[0] == 'b'):
            # Handle special usage (single digit pairwise b terms).
            if (key.count('b') == 1):
                if (len(key) != 3): raise(AmbiguousTerm(f"Interaction term '{key}' is unclear, for >1 digit numbers use 'b#b#' specification."))
                i1, i2 = map(int, key[1:])
                i1, i2 = min(i1,i2), max(i1,i2)
                return super().__setitem__(f"b{i1}b{i2}", value, *args, **kwargs)
            # Handle general interaction usage (pairwise b terms).
            elif (key.count('b') == 2):
                i1, i2 = map(int, key[1:].split('b'))
                i1, i2 = min(i1,i2), max(i1,i2)
                return super().__setitem__(f"b{i1}b{i2}", value, *args, **kwargs)
            else: raise UsageError(f"Provided term '{key}' has too many b's.")
        # Handle a constant coefficient added to the whole system energy.
        elif (key[0] == 'c'): super().__setitem__(key, value, *args, **kwargs)
        # Handle tuple-index accessing.
        elif (len(key) == 2) and (type(key) == tuple) and all(type(v) == int for v in key):
            if key[0] == key[1]:
                return super().__setitem__(f"a{key[0]+1}", value, *args, **kwargs)
            i1, i2 = min(key), max(key)
            return super().__setitem__(f"b{i1+1}b{i2+1}", value, *args, **kwargs)
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
        min_val = float('inf')
        max_val = -float('inf')
        for i in range(bits):
            row = []
            for j in range(0,i):
                v = self.get(f'b{j+1}b{i+1}', 0)
                min_val = min(v, min_val)
                max_val = max(v, max_val)
                if (v != 0) and log: v = int(round(math.log(abs(v),2))) * (-1 if v < 0 else 1)
                if (type(v) == int): row.append( str(v) )
                else:                row.append( f"{v: .2f}" )
            v = self.get(f'a{i+1}', 0)
            min_val = min(v, min_val)
            max_val = max(v, max_val)
            if (v != 0) and log: v = int(round(math.log(v,2))) * (-1 if v < 0 else 1)
            if (type(v) == int): row.append( str(v) )
            else:                row.append( f"{v: .2f}" )
            rows.append( row )
            # Update the column widths.
            for i,v in enumerate(row): col_widths[i] = max(len(v), col_widths[i])

        for i in range(len(rows)):
            rows[i] = "  " + "  ".join([f"{v:^{width}s}" for (v,width) in zip(rows[i], col_widths)])

        max_width = max(map(len, rows))
        return f' QUBO with {bits} bits in range [{min_val}, {max_val}].\n   ' + super().__str__() + '\n ' + '-'*max_width + "\n" + "\n".join(rows) + '\n ' + '-'*max_width
# --------------------------------------------------------------------
