from woocommerce import API
import json
import os
import csv
import subprocess
import pandas as pd

# current working directory of this file
current_directory = os.getcwd()
keyPath = os.path.join(current_directory, "keys.csv") # Create the full path to the CSV file
keys = pd.read_csv(keyPath)

wcapi = API(
    url="https://www.ecoventure.ch",  
    consumer_key = keys.iloc[0, 1], 
    consumer_secret = keys.iloc[1, 1], 
    wp_api=True,  
    version="wc/v3" 
)

# Execute the scraper script
#subprocess.run(["python", "scraper_conda_sh.py"])

# Load the generated ID 
 # Get the current working directory
csv_file_name = "conda.csv" # Specify the CSV file name
csv_file_path = os.path.join(current_directory, csv_file_name) # Create the full path to the CSV file
df = pd.read_csv(csv_file_path) # Read the CSV file into a DataFrame

# Check if column "id" exists
if 'id' not in df.columns:
    # If it doesn't exist, create a new column with no entries
    df['id'] = None

# loop through rows
for index, row in df.iterrows():
    if pd.isnull(row['id']): # only continue if project does not exist yets
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
        "published": 1,
        "images": [
            {"src": row["wpImageLink"],
             "id": row["wpImageID"]}
        ]
        }

        # upload 
        result = wcapi.post("products", data)
        result = result.json()
        
        # add ID to newProducts object
        df.at[index, 'id'] = result['id']
        print(f"INFO: new entry created. ID: {result['id']}")
    else:
        print("INFO: entry already exists")

# save updated csv file
df.to_csv(csv_file_path, index=False)