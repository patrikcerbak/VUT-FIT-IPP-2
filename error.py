import sys


# function for printing an error message and exiting with given error code
def error_exit(string, exit_code):
    sys.stderr.write(string + "\n")
    sys.exit(exit_code)
