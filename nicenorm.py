#!/bin/python3
import subprocess
import sys
import os

def find_exec(program):
    """
    Find the norminette executable in the systems path.

    Parameters
    ----------
    program: str
        the name of the program or the path leading to the program

    Returns
    -------
    str|None
        The absolute path of the executable if a valid executable is found.
    """

    def is_executable(path):
        """
        Checks whether the given path leads to an executable file.

        Parameters
        ---------
        path: str

        Returns
        -------
        bool
        """
        return os.path.isfile(path) and os.access(path, os.X_OK)

    fpath, _ = os.path.split(program)

    # If fpath has a value then the given programname is an path and not just
    # a programs name.
    if fpath and is_executable(fpath):
        return program
    else:
        # Search the entire `path` variable for a folder containing the 
        for path in os.environ["PATH"].split(os.pathsep):
            current = os.path.join(path, program)
            if is_executable(current):
                return current
    return None

class Opts:
    """
    Defines the options which can be given by the user.

    Attributes
    ----------
    nocolor: bool
        If this option is set, no colors will be printed. This is useful for
        writing the output to a file.
    """

    nocolor = False

class Color:
    """
    The values representing the different colors to print certain strings in.

    Attributes
    ----------
    error: str
        The color used for printing errors, so this would not include any norm
        warning.
    warning: str
        The color used to print norminette warnings.
    norme: str
        The color code used to write the "Norme" tag
    reset: str
        The color code used to reset all attributes.
    """

    input_error = "\033[1m\033[31m" # Red
    error = "\033[1m\033[38;5;208m" # Orange
    warning = "\033[1m\033[35m" # Magenta
    norme = "\033[1m" #Bold
    reset = "\033[0m"


def parse_opts(argv):
    """
    Parse the options which can be given by the user. This function will 'cut'
    every element from the argument list which is considered an option. This
    results in an list which can be passed onto the norminette executable.

    Parameters
    ----------
    argv: list
        The argument list passed to the program, including the executable name.

    Returns
    -------
    opts: class Opts
        The options which result from the parsing.
    """

    result = Opts()
    for i in range(len(argv)):
        if argv[i] == "-c" or argv[i] == "--no-color":
            result.nocolor = True
            argv.pop(i)
        else:
            i += 1
    return result

def color_sub(opts, line, substring, color):
    """
    Colors the substring of a given string

    Parameters
    ----------
    opts: class Opts
        The class containing the user specified options.
    line: str
        The line to substitue from
    substring: str
        The substring to color
    color: str
        The color to give to the substring

    Returns
    -------
    str
        The string containing the correct color codes.
    """

    if opts.nocolor:
        return line

    start = line.find(substring)

    if start == -1:
        return line
    
    result = line[0:start]
    result += color
    substrlen = len(substring)
    result += substring
    result += Color.reset
    result += line[start + substrlen:]
    return result


def check_output(opts, output):
    """
    Check the output of the norminette client for any errors concering the
    execution of the program. This does not include norm errors, only stuff
    like invalid options.

    Parameters
    ----------
    opts: class Opts
        The options specified by the user.
    output: list
        The output of the norminette executable as an array of strings.

    Returns
    -------
    bool
        True if any error is found.
    """

    errors = []
    for line in output:
        if line.find("invalid option: ") != -1:
            errors.append(line)

    if len(errors) == 0:
        return False

    print("Input errors returned by norminette:\n")
    for error in errors:
            print(color_sub(opts, error, "invalid option", Color.input_error)
                    .replace("invalid", "Invalid"))
    return True

def cut_empty(output):
    """
    Cut all of the 'empty' norme lines out of the output. This concerns all of
    the lines which correspond to a file in which no norm errors were found.
    Any actual empty lines will be cut aswell.

    Parameters
    ----------
    opts: class Opts
        The options specified by the user.
    output: list
        The output of the norminette executable as an array of strings.
    """
    #TODO: opts

    def contains_norme(line):
        """
        Checks if the given line contains the word "Norme"

        Parameters
        ----------
        line: str

        Returns
        -------
        bool
        """
        return line.find("Norme") != -1
    
    i = 0
    while (True):
        outlen = len(output)
        if i >= outlen:
            break
        if (len(output[i]) == 0) or\
                (output[i].find("Found no changes, using resolution from the lockfile") != -1) or\
                (contains_norme(output[i]) and contains_norme(output[i + 1])):
            output.pop(i)
        else:
            i += 1

    last_index = len(output) - 1
    if len(output[last_index]) == 0 or contains_norme(output[last_index]):
        output.pop(last_index)

def format_nice(opts, output):
    """
    Apply some nice formatting to the norminette output, such as tabluations
    and colors.

    Parameters
    ----------
    opts: class Opts
        The options specified by the user.
    output: list
        The output of the norminette executable as an array of strings.
    """

    for i in range(0, len(output)):
        if (i > 0):
            output[i] = output[i].replace("Norme:", "\nNorme:")
        output[i] = output[i].replace("Error", "\tError")
        output[i] = output[i].replace("Warning", "\tWarning")
        output[i] = color_sub(opts, output[i], "Norme", Color.norme)
        output[i] = color_sub(opts, output[i], "Error", Color.error)
        output[i] = color_sub(opts, output[i], "Warning", Color.warning)

def main():
    # generate our own list of arguments to pass to the norminette executable
    argv = sys.argv.copy()
    opts = parse_opts(argv)

    # find the executable path
    executable = find_exec("norminette")
    if not executable:
        print("No norminette executable found.\n\
You can install the norminette client from this repo: \
https://github.com/hivehelsinki/norminette-client", file=sys.stderr)
        exit(1)

    # execute norminette and get the output
    argv[0] = executable
    process_out = subprocess.Popen(argv,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT)
    output, _ = process_out.communicate()
    output = output.decode("utf-8")

    # split the output into lines
    output = output.split("\n")
    if check_output(opts, output):
        exit(1)

    # cut out all of the lines representing files without errors
    cut_empty(output)

    format_nice(opts, output)

    if len(output) == 0:
        print("No errors found!")
    else:
        for line in output:
            print(line)

if __name__ == "__main__":
    main()
