from woocommerce import API
import os
import pandas as pd
from datetime import datetime

def update_products():
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

    # Load the generated ID 
    # Get the current working directory
    csv_file_name = "conda.csv" # Specify the CSV file name
    csv_file_path = os.path.join(current_directory, csv_file_name) # Create the full path to the CSV file
    df = pd.read_csv(csv_file_path)

    # Check if column "id" exists
    if 'lastUpdate' not in df.columns:
        # If it doesn't exist, create a new column with no entries
        df['lastUpdate'] = None

    # loop through rows
    for index, row in df.iterrows():
        if not pd.isnull(row['id']) and row["published"] == 1: # only create product if there is no ID yet
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
                "id": row["wpImageID"]}
            ]
            }

            # upload 
            update = wcapi.put(f"products/{row['id']}" , data).json()
            
            # add ID to newProducts object
            df.at[index, 'lastUpdate'] = datetime.now()
            print(f"INFO: project updated. ID: {row['id']}")
        if not pd.isnull(row['id']) and row["published"] == 0: # delete project if status was set to 0
            delete = wcapi.delete(f"products/{row['id']}", params={"force": True}).json() # delete
            print(f"INFO: project deleted. ID: {row['id']}")
            df.at[index, 'id'] = None # remove id from csv


    # save updated csv file
    df.to_csv(csv_file_path, index=False)

if __name__ == "__main__":
    
    #import subprocess
    # Execute the scraper script
    #subprocess.run(["python", "scraper_conda_sh.py"])
    
    update_products()