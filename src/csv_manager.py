import os
import pandas as pd
import math

from src.utils import log


# Only these will update
UPDATABLE = ['name', 'image', 'min_investment']

CSV_FNAME = 'projects.csv'

CSV_COLUMNS = {
    'external_link': 'string',
    'published': 'bool',
    ## TODO: implement verfied
    #'verified': 'bool',
    'name': 'string',
    'shortName': 'string',
    'categories': 'string',
    'description': 'string',
    'image': 'string',
    'min_investment': 'string',
    'id': 'float64',
    'lastUpdate': 'str',
    'wpImageLink': 'str',
    'wpImageID': 'float64'
}

def default_value(col):
    if CSV_COLUMNS[col] == 'string' or CSV_COLUMNS[col] == 'str':
        return ''
    elif CSV_COLUMNS[col] == 'bool':
        return False
    elif CSV_COLUMNS[col] == 'float64' or CSV_COLUMNS[col] == 'float':
        return math.nan
    raise Exception(f"default value for dtype `{CSV_COLUMNS[col]}` of column `{col}` not imlemented!")

def update_csv(projects_data):

    log(f'INFO: writing entries to {CSV_FNAME}')

    if os.path.exists(CSV_FNAME):
        df = pd.read_csv(CSV_FNAME)
    else:
        df = pd.DataFrame(columns=list(CSV_COLUMNS.keys()))
        for attributes in projects_data:
            row = [(col, [attributes[col]]) if col in attributes else
                   (col, [default_value(col)]) for col, typ in CSV_COLUMNS.items()]
            row = dict(row)
            df = pd.concat([df, pd.DataFrame(row)], ignore_index=True)


    links = df['external_link']
    for attributes in projects_data:
        if attributes['external_link'] in links.values:
            select_row = df['external_link'] == attributes['external_link']
            rows = df.loc[select_row]

            # make sure only one row is there
            assert(len(rows)==1)
            for key in UPDATABLE:
                df.loc[select_row, key] = attributes[key]

        else: # new one!

            row = [(col, [attributes[col]]) if col in attributes else
                   (col, [default_value(col)]) for col, typ in CSV_COLUMNS.items()]
            row = dict(row)
            df = pd.concat([df, pd.DataFrame(row)], ignore_index=True)

    df.to_csv(CSV_FNAME, index=False)

