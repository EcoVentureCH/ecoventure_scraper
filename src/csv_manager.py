import os
import pandas as pd
import math

from src.utils import log

#
# Default Values:
#

# where the csv lives
CSV_FNAME = 'projects.csv'

# the columns that exist in the csv
CSV_COLUMNS = {
    'name':                 'string',
    'name_short':           'string',
    'external_link':        'string',
    'external_image_link':  'string',
    'funding_min':          'string',
    'funding_target':       'string',
    'funding_current':      'string',
    'location':             'string',
    'currency':             'string',
    'description':          'string',
    'description_short':    'string',
    'id':                   'string',
}

# Only these will update
HOT_RELOADABLE = [
    'funding_current'
]

# get the default value for a given column
def default_value(col, avail_columns=CSV_COLUMNS):
    if avail_columns[col] == 'string' or avail_columns[col] == 'str':
        return ''
    elif avail_columns[col] == 'bool':
        return False
    elif avail_columns[col] == 'float64' or avail_columns[col] == 'float':
        return math.nan
    raise Exception(f"default value for dtype `{avail_columns[col]}` of column `{col}` not imlemented!")

# update the csv if anything changed. only hot_reloadble columns will get updated. returns True if csv changed.
def update_csv(projects_data, csv_filename=CSV_FNAME, hot_reloadable=HOT_RELOADABLE, csv_available_columns=CSV_COLUMNS):

    dirty = False # will be dirty if anything changed, so we can later write the file if dirty.

    if os.path.exists(csv_filename):
        df = pd.read_csv(csv_filename)
    else:
        # we create the csv, because it doesn't exist
        dirty = True
        df = pd.DataFrame(columns=list(csv_available_columns.keys()))
        for attributes in projects_data:
            row = [(col, [attributes[col]]) if col in attributes else
                   (col, [default_value(col, csv_available_columns)]) for col, typ in csv_available_columns.items()]
            row = dict(row)
            df = pd.concat([df, pd.DataFrame(row)], ignore_index=True)

    links = df['external_link']
    for attributes in projects_data:
        if attributes['external_link'] in links.values:
            select_row = df['external_link'] == attributes['external_link']
            rows = df.loc[select_row]

            # make sure only one row is there
            assert(len(rows)==1)
            for key in hot_reloadable:
                if (df.loc[select_row, key] != attributes[key]).all():
                    dirty = True
                    df.loc[select_row, key] = attributes[key]

        else: # new one!
            dirty = True
            row = [(col, [attributes[col]]) if col in attributes else
                   (col, [default_value(col, csv_available_columns)]) for col, typ in csv_available_columns.items()]
            row = dict(row)
            df = pd.concat([df, pd.DataFrame(row)], ignore_index=True)

    if dirty:
        log("INFO: updated entries in {}.".format(csv_filename))
        df.to_csv(csv_filename, index=False)
    else:
        log("INFO: nothing new.. {} is already up to date.".format(csv_filename))

    return dirty
