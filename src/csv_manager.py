import os
import pandas as pd

# all except eternal_link
UPDATABLE = ['name', 'image', 'min_investment']
CSV_FNAME = 'projects.csv'

def update_csv(projects_data):

    print(f'INFO: writing entries to {CSV_FNAME}')

    if os.path.exists(CSV_FNAME):
        df = pd.read_csv(CSV_FNAME)
    else:
        df = pd.DataFrame()
        for attributes in projects_data:
            df = pd.concat([df, pd.DataFrame([attributes])], ignore_index=True)

    links = df['external_link']
    for attributes in projects_data:
        if attributes['external_link'] in links.values:
            # update attributes
            rows = df.loc[df['external_link'] == attributes['external_link']]
            assert(len(rows)==1)
            for key in UPDATABLE:
                df.loc[df['external_link'] == attributes['external_link'], key] = attributes[key]
        else:
            df = pd.concat([df, pd.DataFrame([attributes])], ignore_index=True)

    df.to_csv(CSV_FNAME, index=False)