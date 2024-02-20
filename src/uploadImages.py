import os
import pandas as pd
from src.helperFunctions import downloadImage
from src.helperFunctions import imageToBinary
from src.helperFunctions import uploadImageAPI
from src.utils import print_flushed as print


current_directory = os.getcwd()
keyPath = os.path.join(current_directory, "keys.csv") # Create the full path to the CSV file
keys = pd.read_csv(keyPath)

csv_file_name = "conda.csv" # Specify the CSV file name
csv_file_path = os.path.join(current_directory, csv_file_name) # Create the full path to the CSV file

def upload_images():
    df = pd.read_csv(csv_file_path) # Read the CSV file into a DataFrame

    if 'wpImageLink' not in df.columns:
        df['wpImageLink'] = None

    if 'wpImageID' not in df.columns:
        df['wpImageID'] = None

    # download the image and upload to wordpress
    for index, row in df.iterrows():
        if pd.isnull(row['wpImageLink']) and row['published']:
 
            # download the image from the link
            curImage, fileName = downloadImage(row["image"], row["external_link"])
            
            # Convert PIL image object to binary data
            imageBinary = imageToBinary(curImage)

            # indicate path and upload image to wordpress using API
            fileName = os.path.basename(fileName)

            uploadImage, ImageID = uploadImageAPI(image_binary=imageBinary, username=keys.iloc[3,1], 
                                        password=keys.iloc[2,1], fileName=fileName) ## add password (Action password, not normal admin password)

            # add url and id to DataFrame
            df['wpImageLink'] = df['wpImageLink'].astype(str)
            df.at[index, 'wpImageLink'] = uploadImage
            df.at[index, 'wpImageID'] = ImageID
            
            if uploadImage:
                print("Image uploaded successfully!")
                print("Uploaded image URL:", uploadImage)
            else:
                print("ERROR: Failed to upload image.")
        else:
            print("INFO: skipped image for project {}".format(row['id']))
 

    # save updated csv file
    df.to_csv(csv_file_path, index=False)

if __name__ == "__main__":
    upload_images()

