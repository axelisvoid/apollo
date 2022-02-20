RED   = "\033[0;31m"
GREEN = "\033[0;32m"
RESET = "\033[0m"


print_err = lambda msg: print(RED, f"[ ERROR ]: {msg}", RESET)       # Prints a message to the terminal as an error message.
print_suc = lambda msg: print(GREEN, f"[ SUCCESS ]: {msg}", RESET)   # Prints a message to the terminal as a success message.

