import sys, os

# Function for printing the help message.
def print_help_message():
    with open(os.path.join(DIRECTORY, "about", "usage.txt")) as f:
        print(f.read())

# If no arguments were provided, give the usage.
if len(sys.argv) <= float('inf'):
    print_help_message()

