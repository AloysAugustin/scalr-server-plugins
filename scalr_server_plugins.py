#!/usr/bin/env python
#

import sys, argparse, logging
import types

import commands
import scalr_server_config as cfg

def list_commands():
    l = []
    for a in dir(commands):
        if (isinstance(commands.__dict__.get(a), types.ModuleType) and
                hasattr(commands.__dict__.get(a), 'process') and
                hasattr(commands.__dict__.get(a), 'setup_parser')):
            l.append(a)
    return l

def add_parser(command, subparsers):
    mod = commands.__dict__.get(command)
    parser = subparsers.add_parser(command)
    return getattr(mod, 'setup_parser').__call__(parser)

def make_subparsers_help(parser):
    return 'Command to execute. One of {}. Run "{} <command> --help" to get command-specific help.'.format(
            ', '.join(list_commands()),
            parser.prog
        )

def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    config = cfg.ScalrServerPluginsConfiguration()
    if not config.checkConfig():
        logging.error("Configuration is incorrect")
        return

    mod = commands.__dict__.get(args.command)
    getattr(mod, 'process').__call__(args, config)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scalr plugin management CLI")
    parser.add_argument('--verbose', '-v', action='count',
                        help='Increase verbosity: -v -> INFO, -vv -> DEBUG', default=0)

    subparsers = parser.add_subparsers(metavar='command', dest='command',
                                       help=make_subparsers_help(parser))
    for command in list_commands():
        add_parser(command, subparsers)

    args = parser.parse_args()

    verbose = min(args.verbose, 2)
    loglevel = {0:logging.WARNING, 
                1:logging.INFO,
                2:logging.DEBUG}[verbose]
    main(args, loglevel)
