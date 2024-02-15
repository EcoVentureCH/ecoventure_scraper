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
    print(f"  {program_name} Command [ARG]")
    print()
    print( "Commands:")
    print( "  start SECONDS    - starts and runs the scraper every [seconds] seconds")
    print( "  stops            - tops the scraper")
    print( "  check-new        - check if any new projects are available")
    print( "  list-projects    - lists all projects and their active state and an id")
    print( "  add-poject ID    - mark the project as active   and add on website")
    print( "  remove-poject ID - mark the project as inactive and remove on website")
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


ids = [0, 1, 2, 3]


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

    elif command == "stop":
        stop()
    
    elif command == "check-new":
        check_new()

    elif command == "list-projects":
        list_projects()

    elif command == "add-project":
        if len(args) == 0:
            print_usage()
            print("ERROR: ID was not provided for start Command")
            exit(1)
        id, _ = shift(args)
        try:
            id = int(id)
        except ValueError:
            print_usage()
            print("ERROR: ID needs to be an integer")
            exit(1)

        if id not in ids:
            if len(ids) > 0:
                print( "Hint: call first list-projects")
                print(f"   {program_name} list-projects")
                print( "Available ids:")
                print(f"  {ids}")
                print( "ERROR: ID not in ids list")

            else:
                print( "Hint: call first:")
                print(f"   {program_name} start SECONDS")
                print( "ERROR: no projects found")
            exit(1)
        
        add_project()

    elif command == "remove-project":
        remove_project()

    else:
        print_usage()
        print(f"ERROR: command unknown: {command}")

else:
    print("ERROR: too many arguments")

