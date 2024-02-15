#!/usr/bin/env python3
import sys
from sys import exit
import src.scraper_daemon as scraper_daemon
from src.utils import print_with_color as print

'''daemon interaction'''

ids = [0, 1, 2, 3] # stub

def start(seconds):
    scraper_daemon.restart_daemon(seconds)

def stop():
    scraper_daemon.stop_daemon()

def check_new():
    raise NotImplementedError

def list_projects():
    raise NotImplementedError

def add_project(id):
    raise NotImplementedError

def remove_project(id):
    raise NotImplementedError


if __name__ == "__main__":

    '''Handle command line arguments'''

    def shift(args):
        return args[0], args[1:]

    args = sys.argv
    program_name, args = shift(args)

    def print_description():
        print()
        print( "Scraper Service CLI by ecoventure.ch")
        print( "Command line interface to interact with the scraping service.")
        print()

    def print_usage():
        print( "Usage:")
        print(f"  {program_name} Command [ARG]")
        print()
        print( "Commands:")
        print( "  start SECONDS    - starts and runs the scraper every SECONDS seconds")
        print( "  stop             - stops the scraper")
        print( "  check-new        - check if any new projects are available")
        print( "  list-projects    - lists all projects and their active state and an id")
        print( "  add-poject ID    - mark the project as active   and add on website")
        print( "  remove-poject ID - mark the project as inactive and remove on website")
        print( "  --help           - display help message")
        print()


    if len(args) == 0:
        print_usage()
        print( "ERROR: No Command was provided")

    elif 3 > len(args) > 0:
        command, args = shift(args)
        command = command.lower()
        if command == "--help":
            print_description()
            print_usage()
        elif command == "start":
            if len(args) == 0:
                print_usage()
                print("ERROR: SECONDS was not provided for 'start' Command")
                exit(1)
            seconds, _ = shift(args)
            try:
                seconds = int(seconds)
            except ValueError:
                print_usage()
                print("ERROR: SECONDS needs to be an integer")
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
                print("ERROR: ID was not provided for 'start' Command")
                exit(1)

            id, args = shift(args)
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
            print(f"ERROR: unknown Command '{command}'")

    else:
        print_usage()
        print("ERROR: too many arguments")

