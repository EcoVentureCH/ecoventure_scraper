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

def update_projects():

    df = pd.read_csv(csv_file_path)

    # Check if column "id" exists
    if 'id' not in df.columns:
        df['id'] = None

    if 'published' not in df.columns:
        df['published'] = False

    if 'lastUpdate' not in df.columns:
        df['lastUpdate'] = None

    # loop through rows
    for index, row in df.iterrows():

        # only create product if there is no ID yet and published set
        if pd.isnull(row['id']) and row["published"]: 
            id = create_project(row)
            df.at[index, 'id'] = id
            df.at[index, 'lastUpdate'] = str(datetime.now())

        # remove projects from website
        if not pd.isnull(row['id']) and not row["published"]:
            delete_project(row)
            df.at[index, 'id'] = None
            df.at[index, 'lastUpdate'] = str(datetime.now())


    # save updated csv file
    df.to_csv(csv_file_path, index=False)


def create_project(row):
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
    update = wcapi.put(f"products" , data)
    id = update['id']
    print(f"INFO: new project added. ID: {id}")
    return id


def delete_project(row):
    id = row['id']
    assert(id is not None)
    response = wcapi.delete(f"products/{id}", params={"force": True}).json()
    print(f"INFO: project deleted. ID: {id}")


def delete_inactive_projects():
    csv_file_name = "conda.csv" # Specify the CSV file name
    csv_file_path = os.path.join(current_directory, csv_file_name) # Create the full path to the CSV file
    df = pd.read_csv(csv_file_path)

    for index, row in df.iterrows():
        if pd.isnull(row['published']):
            delete_project(row['id'])



if __name__ == "__main__":
    update_projects()