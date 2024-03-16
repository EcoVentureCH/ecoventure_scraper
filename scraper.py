#!/usr/bin/env python3
import os
import sys
from sys import exit
import pandas as pd

from src.wc_projects import update_projects
from src.wc_images import upload_images

from src.utils import log_c as print
from src.utils import fmt_red, fmt_green, fmt_orange

from src.csv_manager import CSV_FNAME, CSV_COLUMNS

def load_csv():
    if not os.path.exists(CSV_FNAME):
        error_no_csv()
        exit(1)

    df = pd.read_csv(CSV_FNAME, dtype=CSV_COLUMNS)
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
    separator = '  '
    header_id_name = '<id>'
    columns_to_print = {
        'published': '<published>',
        'id': '<WP id>',
        'lastUpdate': '<last modified>',
        'shortName': '<short name>',
        'external_link': '<external link>',
    }

    print()
    print('Listing all projects:')
    offsets = [max(len(df), len(header_id_name))]
    for name, header_print in columns_to_print.items():
        series = df[name]
        l = max(len(header_print), max(series.apply('{}'.format).apply(len)))
        offsets.append(l)

    header_formated = [header_id_name.ljust(offsets[0])] + [head.ljust(l) for l, head in zip(offsets[1:], columns_to_print.values())]
    print(separator.join(header_formated))
        
    for index, row in df.iterrows():
        color = fmt_orange
        if row['published'] == False and pd.isnull(row['id']):
            color = fmt_red
        if row['published'] == True and not pd.isnull(row['id']):
            color = fmt_green
    
        justified_and_colored = [color.format(f'{index}'.ljust(offsets[0]))]  
        for i, field in enumerate(columns_to_print.keys()):
            colored = color.format(f'{row[field]}'.ljust(offsets[i+1]))
            justified_and_colored.append(colored)

        print(separator.join(justified_and_colored))

    print()
    hint_publish()

def add_all_projects(df):
    for index, row in df.iterrows():
        if row['published'] == False:
            df.loc[index, 'published'] = True
            print(f"INFO: marked project {index} for publishing.")
    return df

def remove_all_projects(df):
    for index, row in df.iterrows():
        if row['published'] == True:
            df.loc[index, 'published'] = False
            print(f"INFO: marked project {index} for removal.")
    return df

def add_project(id_here, df):
    for index, row in df.iterrows():
        if index == id_here:
            published = row['published']
            if published == True:
                print(f'ERROR: already published project {id_here}')
                exit(1)
            else:
                df.loc[id_here, 'published'] = True
                print(f"INFO: marked project {id_here} for publishing.")
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
                print(f"INFO: marked project {id_here} for removal.")
                return df
    else:
        assert False, 'unreachable'

### CLI Subcommands bindings

class Subcommand:
    def __init__(self, name, description, run, signature = '') -> None:
        self.name = name
        self.run = run
        self.description = description
        self.signature = signature

def subc_help(args):
    print_description()
    print_usage()

def subc_start(args):
    if len(args) == 0:
        print(f"ERROR: <seconds> was not provided for start Command")
        exit(1)
    elif len(args) == 1:
        seconds = args[0]
        try:
            seconds = int(seconds)
        except ValueError:
            print("ERROR: <seconds> needs to be an integer")
            exit(1)

    else:
        print("ERROR: too many arguments for 'start' Command")
        exit(1)

    start(seconds)

def subc_status(args):
    from src.scraper_daemon import get_pid
    pid = get_pid()
    if pid >= 0:
        print(f"INFO: status: daemon running PID={pid}")
    else:
        print(f"INFO: status: daemon not runnning")

def subc_stop(args):
    stop()

def subc_list(args):
    df = load_csv()
    list_projects(df)

def subc_publish(args):
    upload_images()
    update_projects()

def subc_add(args):
    df = load_csv()
    valid_ids = list(range(len(df)))

    if len(args) == 0:
        print_usage()
        print("ERROR: ID was not provided for 'add' Command")
        exit(1)

    if len(args) == 1 and args[0] == '--all':
        df = add_all_projects(df)
        df.to_csv(CSV_FNAME, index=False)
        return

    ids = parse_ids_from_args(args, valid_ids)
    for id in ids:
        df = add_project(id, df)

    df.to_csv(CSV_FNAME, index=False)


def subc_remove(args):
    df = load_csv()
    valid_ids = list(range(len(df)))

    if len(args) == 0:
        print_usage()
        print("ERROR: ID was not provided for 'remove' Command")
        exit(1)

    if len(args) == 1 and args[0] == '--all':
        df = remove_all_projects(df)
        df.to_csv(CSV_FNAME, index=False)
        return

    ids = parse_ids_from_args(args, valid_ids)
    for id in ids:
        df = remove_project(id, df)

    df.to_csv(CSV_FNAME, index=False)


### CLI Subcommands

available_subcommands = [
    Subcommand('start', 'starts the scraper (runs every <seconds> seconds)', run=subc_start, signature='<seconds>'),
    Subcommand('stop', 'stops the scraper', run=subc_stop),
    Subcommand('status', 'check if the scraper is running', run=subc_status),
    Subcommand('list', 'lists all projects and their state', run=subc_list),
    Subcommand('add', 'mark project[s] as active', run=subc_add, signature='<id> [<id> ...] | --all'),
    Subcommand('remove', 'mark project[s] as inactive', run=subc_remove, signature='<id> [<id> ...] | --all'),
    Subcommand('publish', 'apply del/add-ed to website', run=subc_publish),
    Subcommand('help', 'display help message', run=subc_help),
]

if __name__ == "__main__":

    args = sys.argv
    program_name, *args = args

    def error_no_csv():
        print( "Hint: to start the scraper call")
        print(f"   {program_name} start SECONDS")
        print(f"ERROR: {CSV_FNAME} not found")

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
        print(f"   {program_name} <subcommand> [...]")
        print()
        print( "subcommands:")
        left_width = max([len(f'{subc.name} {subc.signature}') for subc in available_subcommands])
        for subc in available_subcommands:
            command_str = f'{subc.name} {subc.signature}'.ljust(left_width)
            print(f"    {command_str} - {subc.description}")
        print()

    def parse_ids_from_args(args, valid_ids):
        ids = []
        for arg in args:
            try:
                id = int(arg)
            except ValueError:
                print( "IDs Available:")
                print(f"    {ids}")
                print(f"ERROR: <id> {arg} needs to be an integer")
                exit(1)
            if id not in valid_ids:
                if len(ids) > 0:
                    print( "Hint: call list to see projects")
                    print(f"    {program_name} list")
                    print( "IDs Available:")
                    print(f"    {ids}")
                    print(f"ERROR: project with <id> {id} not found")
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
        command, *args = args
        command = command.lower()

        available_subcommands_dict = {sc.name: sc for sc in available_subcommands}

        if command not in available_subcommands_dict.keys():
            print_usage()
            print(f"ERROR: unknown Command '{command}'")
            exit(1)

        available_subcommands_dict[command].run(args)

    else:
        print_usage()
        print("ERROR: too many arguments")
