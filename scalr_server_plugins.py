#!/usr/bin/env python
#

# import modules used here -- sys is a very standard one
import sys, argparse, logging
import types
import commands
from commands import *

def list_commands():
    l = []
    for a in dir(commands):
        if (isinstance(commands.__dict__.get(a), types.FunctionType) or
            isinstance(commands.__dict__.get(a), types.ModuleType)):
            l.append(a)
    return l
    pass

# Gather our code in a main() function
def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)
    cmdString = args.cmd[0]
    args.cmd.pop(0)
    cmd = commands.__dict__.get(cmdString)
    if isinstance(cmd,types.ModuleType):
        getattr(cmd, 'process').__call__(args.args, loglevel)
    elif isinstance(cmd, types.FunctionType):
        cmd.__call__(args.args, loglevel)
    else:
        raise StandardError("Not Implemented")


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Scalr plugin management CLI"
    )
    parser.add_argument(
        "cmd",
        nargs=1,
        help="Execute COMMAND",
        metavar="COMMAND"
        )
    parser.add_argument(
        'args',
        nargs=argparse.REMAINDER)

    args = parser.parse_args()
    loglevel = logging.INFO
    main(args, loglevel)
