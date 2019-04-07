# Return all unique primes less than or equal to a number.
def primes_up_to(num):
    # Search function for telling if a number is prime.
    def is_prime(num):
        for i in range(2,int(num**(1/2))+1):
            if ((num % i) == 0): return False
        return True
    # Search for generating all primes up to a number.
    return [1] + [i for i in range(2,num) if is_prime(i)]

