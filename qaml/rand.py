
# Custom excepion for improper user-specified ranges.
class InvalidRange(Exception):
    def __init__(self, start, stop, step, count):
        return super().__init__("\n\nError: random_range(start=%s,stop=%s,step=%s)[:count=%s] contains no elements."%(start,stop,step,count))

# Return a randomized "range" using the appropriate technique based on
# the size of the range being generated. If the memory footprint is
# small (<= 32KB) then a random sample is created and returned.
# If the memory footprint would be prohibitively large, a Linear
# Congruential Generator is used to efficiently generate the sequence.
# 
# Parameters are similar to the builtin `range` with:
#   start -- int, default of 0.
#   stop  -- int > start for no / positive step, < start otherwise.
#   step  -- int (!= 0), default of 1.
#   count -- int > 0, number of samples, default (stop-start)//step.
# 
# Usage (and implied parameter ordering):
#   random_range(a)             --> range(0, a, 1)[:a]
#   random_range(a, b)          --> range(a, b, 1)[:b-a]
#   random_range(a, b, c)       --> range(a, b, c)[:(b-a)//c]
#   random_range(a, b, c, d)    --> range(a, b, c)[:d]
#   random_range(a, d) [d <= a] --> range(0, a, 1)[:d]
# 
# If the size of the range is large, a Linear Congruential Generator is used.
#   Memory  -- O(1) storage for a few integers, regardless of parameters.
#   Compute -- O(n) at most 2 times the number of steps in the range, n.
# 
def random_range(start, stop=None, step=None, count=float('inf')):
    from random import sample, randint
    from math import ceil, log2
    # Add special usage where the second argument is meant to be a count.
    if (stop != None) and (stop <= start) and ((step == None) or (step >= 0)):
        start, stop, count = 0, start, stop
    # Set a default values the same way "range" does.
    if (stop == None): start, stop = 0, start
    if (step == None): step = 1
    # Compute the number of numbers in this range, update count accordingly.
    num_steps = (stop - start) // step
    count = min(count, num_steps)
    # Check for a usage error.
    if (num_steps == 0) or (count <= 0): raise(InvalidRange(start, stop, step, count))
    # Use robust random method if it has a small enough memory footprint.
    if (num_steps <= 2**15):
        for value in sample(range(start,stop,step), count): yield value
        return
    # Use the LCG for the cases where the above is too memory intensive.
    # Use a mapping to convert a standard range into the desired range.
    mapping = lambda i: (i*step) + start
    # Seed range with a random integer to start.
    value = randint(0,num_steps)
    # 
    # Construct an offset, multiplier, and modulus for a linear
    # congruential generator. These generators are cyclic and
    # non-repeating when they maintain the properties:
    # 
    #   1) "modulus" and "offset" are relatively prime.
    #   2) ["multiplier" - 1] is divisible by all prime factors of "modulus".
    #   3) ["multiplier" - 1] is divisible by 4 if "modulus" is divisible by 4.
    # 
    offset = randint(0,num_steps) * 2 + 1                 # Pick a random odd-valued offset.
    multiplier = 4*(num_steps + randint(0,num_steps)) + 1 # Pick a multiplier 1 greater than a multiple of 4.
    modulus = 2**ceil(log2(num_steps))                    # Pick a modulus just big enough to generate all numbers (power of 2).
    # Track how many random numbers have been returned.
    found = 0
    while found < count:
        # If this is a valid value, yield it in generator fashion.
        if value < num_steps:
            found += 1
            yield mapping(value)
        # Calculate the next value in the sequence.
        value = (value*multiplier + offset) % modulus
