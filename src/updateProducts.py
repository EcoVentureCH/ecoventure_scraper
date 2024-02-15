from woocommerce import API
import os
import pandas as pd
from datetime import datetime
from src.utils import print_flushed as print

# current working directory of this file
current_directory = os.getcwd()
csv_file_name = "conda.csv"
csv_file_path = os.path.join(current_directory, csv_file_name) # Create the full path to the CSV file
keyPath = os.path.join(current_directory, "keys.csv") # Create the full path to the CSV file
keys = pd.read_csv(keyPath)

wcapi = API(
    url="https://www.ecoventure.ch",  
    consumer_key = keys.iloc[0, 1], 
    consumer_secret = keys.iloc[1, 1], 
    wp_api=True,  
    version="wc/v3" 
)

def update_products():

    df = pd.read_csv(csv_file_path)

    # Check if column "id" exists
    if 'id' not in df.columns:
        df['id'] = None

    if 'published' not in df.columns:
        df['published'] = None

    if 'lastUpdate' not in df.columns:
        df['lastUpdate'] = None

    # loop through rows
    for index, row in df.iterrows():
        if not pd.isnull(row['id']) and row["published"] == 1: # only create product if there is no ID yet
            create_project(row['id'], df)
            df.at[index, 'lastUpdate'] = str(datetime.now())


        if not pd.isnull(row['id']) and row["published"] == 0: # delete project if status was set to 0
            delete_project(row['id'], df)

    # save updated csv file
    df.to_csv(csv_file_path, index=False)


def create_project(id, df: pd.DataFrame):
    row = df.loc[df['id'] == id].iloc[0]
    index = df.index[df['id'] == id][0]

    # Access values of each column for the current row
    data = {
        "name": row["name"],
        "meta_data": [
            {
            "key": "wpneo_funding_minimum_price",
            "value": row["min_investment"]
            },
            {
            "key": "krowd_project_link",
            "value" : row['external_link']
            }
        ],
        "type": "crowdfunding",
        "images": [
            {"src": row["wpImageLink"],
            "id": float(row["wpImageID"])}
        ]
    }

    # upload
    update = wcapi.put(f"products/{id}" , data)
    print(update)
    
    # add ID to newProducts object
    print(f"INFO: new project added. ID: {row['id']}")


def delete_project(id, df):
    response = wcapi.delete(f"products/{id}", params={"force": True}).json()
    print(f"INFO: project deleted. ID: {int(df[df['id'] == id]['id'].iloc[0])}")


def delete_inactive_projects():
    csv_file_name = "conda.csv" # Specify the CSV file name
    csv_file_path = os.path.join(current_directory, csv_file_name) # Create the full path to the CSV file
    df = pd.read_csv(csv_file_path)

    for index, row in df.iterrows():
        if not pd.isnull(row['published']) == 0:
            delete_project(row['id'])



if __name__ == "__main__":
    
    #import subprocess
    # Execute the scraper script
    #subprocess.run(["python", "scraper_conda_sh.py"])
    
    update_products()