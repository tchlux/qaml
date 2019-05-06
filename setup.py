# Personal account token string (https://cloud.dwavesys.com/leap/) for
# running experiments on real DWAVE system.
token = ""

if (len(token) == 0):
    class UnregisteredAccount(Exception): pass
    raise(UnregisteredAccount("Store your API token string in the 'token' variable after registering an account with DWAVE Leap."))
