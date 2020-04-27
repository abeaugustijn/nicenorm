# nicenorm
_Better output from 42 schools' norminette_

The goal of this project is to make the output of norminette more readable and extract only the useful information.

![Example image](/example.jpg)
_(left side is norminette, right side is nicenorm)_

## Installation
`install.sh` can be run to install nicenorm on your system. The script will copy the source file to `$HOME/.bin`. Make sure this path is present in your `$PATH` variable. 

### Prerequisites
To use nicenorm, the following packages are required:
* A norminette client. This can be either the one installed on the macs in your local cluster, or the one published by Hive Helsinki: https://github.com/hivehelsinki/norminette-client
* python3 (is probably already installed on your system)

## Features
* Color highlighting
* Better readability
* Ignore files without errors or warnings

## Todo
Some things that will be added soon.
* The ability to ignore warnings
* Better argument parsing
* Handle more norminette errors

Please open an issue for any discrepancies you encounter or features you'd like to see in the future.
