#!/usr/bin/env python3
import os
import sys
from sys import exit
import src.scraper_daemon as scraper_daemon
from src.utils import print_with_color as print
from src.utils import fmt_red, fmt_green
import pandas as pd

from src.updateProducts import create_project, delete_project
from src.updateProducts import update_products

CSV_FNAME = 'conda.csv'

'''daemon interaction'''
def start(seconds):
    scraper_daemon.restart_daemon(seconds)

def stop():
    scraper_daemon.stop_daemon()

'''csv interaction'''
def check_new():
    raise NotImplementedError

def list_projects(df):
    print('Listing all projects')
    print('   id    - published - last accessed              - link')
    for index, row in df.iterrows():
        id = int(row['id'])
        lu = row['lastUpdate']
        link = row['external_link']
        if row['published'] == 0 or pd.isnull(row['published']):
            id = fmt_red.format(id)
            publ = 'no '
        else:
            id = fmt_green.format(id)
            publ = 'yes'
        print(f"   {fmt_red.format(id)} - {publ}       - {lu} - {link}")

def add_project(id, df):
    published = df.loc[df['id'] == id, 'published'].iloc[0]

    if pd.isnull(published) or published == 0:
        df.loc[df['id'] == id, 'published'] = 1
        create_project(id, df)
    else:
        print(f"ERROR: project with ID {id} is already added")
        exit(1)
    return df

def remove_project(id, df):
    published = df.loc[df['id'] == id, 'published'].iloc[0]
    if not pd.isnull(published) or published == 1:
        delete_project(id, df)
        df.loc[df['id'] == id, 'published'] = 0
    else:
        print(f"ERROR: project with ID {id} is already removed")
        exit(1)
    return df

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
        print( "  status           - check if the scraper is running")
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

        elif command == 'status':
            pid = scraper_daemon.get_pid()
            if pid >= 0:
                print(f"status: daemon running PID={pid}")
            else:
                print(f"status: daemon not runnning")


        elif command == "stop":
            stop()
        
        elif command == "check-new":
            check_new()

        elif command == "list-projects":
            df = pd.read_csv(CSV_FNAME)
            list_projects(df)

        elif command == "add-project":
            if len(args) == 0:
                print_usage()
                print("ERROR: ID was not provided for 'add-project' Command")
                exit(1)

            id, args = shift(args)
            try:
                id = int(id)
            except ValueError:
                print_usage()
                print("ERROR: ID needs to be an integer")
                exit(1)

            df = pd.read_csv(CSV_FNAME)
            ids = list(map(int, df['id'].to_list()))

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
            
            df = add_project(id, df)
            df.to_csv(CSV_FNAME, index=False)

        elif command == "remove-project":
            if len(args) == 0:
                print_usage()
                print("ERROR: ID was not provided for 'remove-project' Command")
                exit(1)

            id, args = shift(args)
            try:
                id = int(id)
            except ValueError:
                print_usage()
                print("ERROR: ID needs to be an integer")
                exit(1)

            df = pd.read_csv(CSV_FNAME)
            ids = list(map(int, df['id'].to_list()))

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

            df = remove_project(id, df)
            df.to_csv(CSV_FNAME, index=False)


        else:
            print_usage()
            print(f"ERROR: unknown Command '{command}'")

    else:
        print_usage()
        print("ERROR: too many arguments")

    
