# Given a QUBO, cycle through the coefficients and yield them from
# this generator funciton.
def cycle_coefs(q, num_bits):
    for i in range(num_bits):
        for j in range(i+1):
            if (i == j): coef = f"a{i+1}"
            else:        coef = f"b{j+1}b{i+1}"
            yield coef

# Return all unique primes less than or equal to a number.
def primes_up_to(num):
    # Search function for telling if a number is prime.
    def is_prime(num):
        for i in range(2,int(num**(1/2))+1):
            if ((num % i) == 0): return False
        return True
    # Search for generating all primes up to a number.
    return [1] + [i for i in range(2,num) if is_prime(i)]

# Define a function that rounds to the nearest power of two.
def round_pow_2(v):
    import math
    return (v/min(1e-10,abs(v))) * 2**round(math.log(max(1,abs(v)),2))
