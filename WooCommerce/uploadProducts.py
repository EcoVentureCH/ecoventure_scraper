from woocommerce import API
import json
import os
import csv
import subprocess
import pandas as pd

wcapi = API(
    url="https://www.ecoventure.ch", 
    consumer_key="", 
    consumer_secret="", 
    wp_api=True,  
    version="wc/v3" 
)

# Execute the scraper script
#subprocess.run(["python", "scraper_conda_sh.py"])

# Load the generated ID 
current_directory = os.getcwd() # Get the current working directory
csv_file_name = "conda.csv" # Specify the CSV file name
csv_file_path = os.path.join(current_directory, csv_file_name) # Create the full path to the CSV file
df = pd.read_csv(csv_file_path) # Read the CSV file into a DataFrame

# add ID column
df["id"] = None

# update the generated csv file with the Product ID (if there is already an existing entry)
...

# select rows where ID is NULL (= new products)
newProducts = df[df["id"].isnull()]

## FOR TESTING - only keep first row
#newProducts = newProducts.head(1)

for index, row in newProducts.iterrows():
    # Access values of each column for the current row
    data = {
    "name": row[" name"],
    "meta_data": [
        {
        "key": "krowd_project_link",
        "value" : row["# external_link"]
        }
    ],
    "type": "crowdfunding",
    "published": 1
    }
    # upload 
    result = wcapi.post("products", data)
    result = result.json()
    print(result['id'])




