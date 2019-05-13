# Personal account token string (https://cloud.dwavesys.com/leap/) for
# running experiments on real DWAVE system.
import os

token_file_name = ".dwave-token"
token_file = os.path.join(os.expanduser("~"), token_file_name)

if not os.path.exists(token_file):
    class UnregisteredAccount(Exception): pass
    raise(UnregisteredAccount("\n\nStore your DWAVE Leap API token string in a file named '.dwave-token' in your home directory.\nGet this token by registering an account with DWAVE Leap."))

# Read the token from a file on the user's computer.
with open(token_file) as f:
    token = f.read().strip()

