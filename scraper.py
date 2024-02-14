#!/usr/bin/env python3
import sys
from sys import exit

_print = print
def print_with_color(*a, **k):
    RED='\033[0;31m'
    NC='\033[0m' # No Color
    if a and a[0].startswith('ERROR:'):
        _print(f"{RED}{a[0]}{NC}" )
    else:
        _print(*a)
print = print_with_color

def shift(args):
    return args[0], args[1:]

args = sys.argv
program_name, args = shift(args)

def print_usage():
    print( "Usage:")
    print(f"  {program_name} Command [Args]")
    print()
    print( "Commands:")
    print( "  start [seconds]    - starts and runs the scraper every [seconds] seconds")
    print( "  stops              - tops the scraper")
    print( "  check-new          - check if any new projects are available")
    print( "  list-projects      - lists all projects and their active state and an id")
    print( "  add-poject [id]    - add the project as active on website")
    print( "  remove-poject [id] - add the project as active on website")
    print()

def start(seconds):
    raise NotImplementedError

def stop():
    raise NotImplementedError

def check_new():
    raise NotImplementedError

def list_projects():
    raise NotImplementedError

def add_project(id):
    raise NotImplementedError

def remove_project(id):
    raise NotImplementedError

if len(args) == 0:
    print_usage()
    print( "ERROR: No Command was provided")



elif 3 > len(args) > 0:
    command, args = shift(args)
    command = command.lower()
    if command == "start":
        if len(args) == 0:
            print_usage()
            print("ERROR: seconds was not provided for start Command")
            exit(1)
        seconds, _ = shift(args)
        try:
            seconds = int(seconds)
        except ValueError:
            print_usage()
            print("ERROR: seconds needs to be an integer")
            exit(1)
        start(seconds)

    else:
        print_usage()
        print(f"ERROR: command unknown: {command}")

else:
    print("ERROR: too many arguments")

