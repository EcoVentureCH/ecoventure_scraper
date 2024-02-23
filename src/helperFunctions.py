# helper functions
import pandas as pd
import requests
import os
from PIL import Image
from io import BytesIO

from src.utils import print_flushed as print

# download image and return as object
def downloadImage(url, externalLink):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print("Image download successfull")
        # Read the image content from the response
        image_content = response.content
        
        # Create an Image object from the image content
        img = Image.open(BytesIO(image_content))
        
        # Return the Image object
        parts = externalLink.split('/')
        # Extract the last element of the list
        filename = parts[-2]
        filename += ".png"
        img.save(filename)
        return img, filename
    else:
        print(f"Failed to download image. Status code: {response.status_code}")
        return None

# Convert PIL image object to binary data
def imageToBinary(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    binary = buffered.getvalue()
    # Close the BytesIO object
    buffered.close()     
    return binary

# Upload image to WordPress media library
def uploadImageAPI(image_binary, username, password, fileName):
    # Construct the authentication credentials
    auth = (username, password)

    # Define the endpoint for media uploads
    endpoint = 'https://ecoventure.ch/wp-json/wp/v2/media' # might need to be updated if version changes

    # Define the headers specifying the content type
    headers = {'Content-Type': 'image/jpeg','Content-Disposition' : 'attachment; filename=%s'% fileName}

    # Send a POST request to upload the image
    response = requests.post(endpoint, auth=auth, headers=headers, data=image_binary)

    # Check if the request was successful (status code 201)
    if response.status_code == 201:
        # Parse the JSON response to get the URL of the uploaded image
        uploaded_image_url = response.json()['source_url']
        uploaded_image_id = response.json()['id']
        # remove the file locally
        os.remove(fileName)
        return uploaded_image_url, uploaded_image_id
    else:
        print(f"Failed to upload image. Status code: {response.status_code}")
        return None