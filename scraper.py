#!/usr/bin/env python3
import os
import sys
from sys import exit
from src.utils import print_with_color as print
from src.utils import fmt_red, fmt_green, fmt_orange
import pandas as pd

from src.updateProducts import update_projects
from src.uploadImages import upload_images

CSV_FNAME = 'conda.csv'

def load_csv():

    if not os.path.exists(CSV_FNAME):
        error_no_csv()
        exit(1)

    df = pd.read_csv(CSV_FNAME, dtype={
        'external_link':'string',
        'name': 'string',
        'shortName': 'string',
        'categories': 'string',
        'description': 'string',
        'image': 'string',
        'min_investment': 'string',
        'id': 'float64',
        'published': 'bool',
        'lastUpdate': 'str',
        'wpImageLink': 'str',
        'wpImageID': 'float64'
    })
    return df

'''daemon interaction'''
def start(seconds):
    import src.scraper_daemon as scraper_daemon
    scraper_daemon.restart_daemon(seconds)

def stop():
    import src.scraper_daemon as scraper_daemon
    scraper_daemon.stop_daemon()

'''csv interaction'''
def list_projects(df):
    print('Listing all projects')
    print('   ID    - published - ext_id - last accessed                - link')
    for index, row in df.iterrows():
        if not pd.isnull(row['id']):
            id = int(row['id'])
        else:
            id = '     '
        lu = row['lastUpdate']
        lu = lu if not pd.isnull(lu) else '                          '
        link = row['external_link']

        if row['published'] == False or pd.isnull(row['published']):
            if pd.isnull(row['id']):
                id_here = fmt_red.format(index)
                publ = fmt_red.format('no     ')
            else:
                id_here = fmt_orange.format(index)
                publ = fmt_orange.format('remove ')
        else:
            if pd.isnull(row['id']):
                id_here = fmt_orange.format(index)
                publ = fmt_orange.format('add    ')
            else:
                id_here = fmt_green.format(index)
                publ = fmt_green.format('yes    ')

        print(f"   {id_here}     - {publ}   - {id}  - {lu}   - {link}")
    print()
    hint_publish()

def add_project(id_here, df):
    for index, row in df.iterrows():
        if index == id_here:
            published = row['published']
            if published == True:
                print(f'ERROR: already published project {id_here}')
                exit(1)
            else:
                df.loc[id_here, 'published'] = True
                return df
    else:
        assert False, 'unreachable'

def remove_project(id_here, df):
    for index, row in df.iterrows():
        if index == id_here:
            published = row['published']
            if published == False:
                print(f'ERROR: already removed project {id_here}')
                exit(1)
            else:
                df.loc[id_here, 'published'] = False
                return df
    else:
        assert False, 'unreachable'



if __name__ == "__main__":

    '''Handle command line arguments'''

    def shift(args):
        return args[0], args[1:]

    args = sys.argv
    program_name, args = shift(args)

    def error_no_csv():
        print( "Hint: to start the scraper call")
        print(f"   {program_name} start SECONDS")
        print( "ERROR: no projects found")

    def hint_publish(): 
        changes = fmt_orange.format('changes')
        print(f"Hint: to publish {changes} run:")
        print(f"   {program_name} publish")
    
    def print_description():
        print()
        print( "Scraper Service CLI of ecoventure.ch")
        print( "Command line interface to interact with the scraping service.")
        print()

    def print_usage():
        print( "Usage:")
        print(f"  {program_name} Command [...]")
        print()
        print( "Commands:")
        print( "  start <SECONDS>        - starts the scraper (runs every <SECONDS> seconds)")
        print( "  stop                   - stops the scraper")
        print( "  status                 - check if the scraper is running")
        print( "  list                   - lists all projects and their state")
        print( "  add    <ID> [<ID>...]  - mark project[s] as active")
        print( "  remove <ID> [<ID>...]  - mark project[s] as inactive")
        print( "  publish                - apply del/add-ed to website")
        print( "  --help                 - display help message")
        print()

    def parse_ids_from_args(args, valid_ids):
        ids = []
        for arg in args:
            try:
                id = int(arg)
            except ValueError:
                print( "IDs Available:")
                print(f"    {ids}")
                print(f"ERROR: ID {arg} needs to be an integer")
                exit(1)
            if id not in valid_ids:
                if len(ids) > 0:
                    print( "Hint: call list to see projects")
                    print(f"    {program_name} list")
                    print( "IDs Available:")
                    print(f"    {ids}")
                    print(f"ERROR: project with ID {id} not found")
                    exit(0)
                else:
                    assert False
            ids.append(id)
        return ids



    if len(args) == 0:
        print_description()
        print_usage()
        print( "ERROR: No Command was provided")


    elif 10 > len(args) > 0:
        command, args = shift(args)
        command = command.lower()
        if command == "--help":
            print_description()
            print_usage()
        elif command == "start":
            if len(args) == 0:
                print("ERROR: <SECONDS> was not provided for 'start' Command")
                exit(1)
            elif len(args) == 1:
                seconds, _ = shift(args)
                try:
                    seconds = int(seconds)
                except ValueError:
                    print("ERROR: <SECONDS> needs to be an integer")
                    exit(1)
            else:
                print("ERROR: too many arguments for 'start' Command")
                exit(1)

            start(seconds)

        elif command == 'status':
            from src.scraper_daemon import get_pid
            pid = get_pid()
            if pid >= 0:
                print(f"INFO: status: daemon running PID={pid}")
            else:
                print(f"INFO: status: daemon not runnning")


        elif command == "stop":
            stop()

        elif command == "list":
            df = load_csv()
            list_projects(df)

        elif command == 'publish':
            upload_images()
            update_projects()

        elif command == "add":
            df = load_csv()
            valid_ids = list(range(len(df)))

            if len(args) == 0:
                print_usage()
                print("ERROR: ID was not provided for 'add' Command")
                exit(1)

            ids = parse_ids_from_args(args, valid_ids)
            for id in ids:
                df = add_project(id, df)

            df.to_csv(CSV_FNAME, index=False)
            if len(ids) == 1:
                print(f"INFO: marked project {ids[0]} for publishing.")
            else:
                print(f"INFO: marked projects {ids} for publishing.")

        elif command == "remove":
            df = load_csv()
            valid_ids = list(range(len(df)))

            if len(args) == 0:
                print_usage()
                print("ERROR: ID was not provided for 'remove' Command")
                exit(1)

            ids = parse_ids_from_args(args, valid_ids)
            for id in ids:
                df = remove_project(id, df)

            df.to_csv(CSV_FNAME, index=False)
            if len(ids) == 1:
                print(f"INFO: marked project {ids[0]} for removal.")
            else:
                print(f"INFO: marked projects {ids} for removal.")


        else:
            print_usage()
            print(f"ERROR: unknown Command '{command}'")

    else:
        print_usage()
        print("ERROR: too many arguments")

    
