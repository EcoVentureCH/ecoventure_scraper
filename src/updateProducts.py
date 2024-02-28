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

    if 'shortName' not in df.columns:
        df['shortName'] = None
    
    if 'categories' not in df.columns:
        df['categories'] = None

    if 'description' not in df.columns:
        df['description'] = None

    # loop through rows
    for index, row in df.iterrows():

        # remove projects from website
        if not pd.isnull(row['id']) and not row["published"]:
            delete_project(row)
            df.at[index, 'id'] = None
            df['lastUpdate'] = df['lastUpdate'].astype(str)
            df.at[index, 'lastUpdate'] = str(datetime.now())

        # only create product if there is no ID yet and published set
        if pd.isnull(row['id']) and row["published"]: 
            id = create_project(row)
            df.at[index, 'id'] = id
            df['lastUpdate'] = df['lastUpdate'].astype(str)
            df.at[index, 'lastUpdate'] = str(datetime.now())

    # save updated csv file
    df.to_csv(csv_file_path, index=False)

def returnCategories(row):
    # get all categories from wordpress
    allCategories = wcapi.get("products/categories").json()
    
    # only keep entries that are in row | return name and id of category and remove other keys
    filteredCat = [d for d in allCategories if d['name'] in row]
    filteredCat = [{k: v for k, v in d.items() if k in ['name', 'id']} for d in filteredCat]

    #to do: impelement a check that warns user that Category does not exist yet (or typo)

    return filteredCat

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
    # appends additional information if exists (description, shortName, category)
    if pd.notna(row['description']) and row['description']:
        data["description"] = row["description"]
    if pd.notna(row['shortName']) and row['shortName']:
        data["name"] = row["shortName"] # overwrites long name
    if pd.notna(row["categories"]) and row["categories"]:
        data["categories"] = returnCategories(row = row["categories"])

    # upload
    update = wcapi.post("products" , data).json()
    id = update['id']
    print(f"INFO: new project added. ID: {id}")
    return id

def delete_project(row):
    id = int(row['id'])
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
