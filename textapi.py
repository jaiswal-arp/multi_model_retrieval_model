import os
import boto3
import base64
import openai
import requests
import json
import time
from dotenv import load_dotenv



# Load AWS credentials from .env file
load_dotenv()


# Get AWS credentials from environment variables
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
s3_bucket_name = 'fashionimages05'

# AWS S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# Prompt 
fashion_navigation = (
    "YOUR ROLE:\n"
    "Imagine you are a fashion navigation expert tasked with reviewing the navigation bar "
    "of leading online retail websites such as Macy's or Amazon. Your goal is to generate "
    "a comprehensive list of tags or annotations for similar fashion products. This information "
    "will be used to optimize user search and enhance the recommendation algorithm.\n\n"
    "UNDERSTANDING:\n"
    "Provide an overview of your understanding regarding the navigation bar of these websites. "
    "Consider the types of fashion products, user demographics, and any key features that stand out.\n\n"
    "TAGGING:\n"
    "Generate a list of at least 11 annotations or tags that would be valuable for someone searching "
    "for fashion products on these websites. Think about how these tags can contribute to an improved user "
    "experience and enhance the efficiency of the recommender algorithm.\n\n"
    "Please respond with your annotations in a JSON format:\n\n"
    "{\n"
    "  \"navigation_tags\": [\n"
    "    \"{{ Tag 1 }}\",\n"
    "    \"{{ Tag 2 }}\",\n"
    "    // ... additional tags, at least 11 in total\n"
    "  ]\n"
    "}\n"
    "You MUST ONLY output JSON; no other text is permitted.\n"
)

# Set the OpenAI API key from environment variables
openai.api_key = os.environ['OPENAI_API_KEY']

# Filename to save responses
filename = 'responses.json'

# Function to encode an image
def encode_image(image_content):
    return base64.b64encode(image_content).decode('utf-8')

# Function to save response content
def save_response_content(image_name, content):
    data = {
        "image": image_name,
        "response_content": content
    }

    filename = 'responses.json'
    # Check if file exists and has content
    try:
        with open(filename, 'r+') as file:
            # Read current data from file
            file_data = json.load(file)
            # Append new data
            file_data.append(data)
            # Set file's current position at offset
            file.seek(0)
            # Update JSON file
            json.dump(file_data, file, indent=4)
    except (FileNotFoundError, json.JSONDecodeError):
        # Create new file with initial data
        with open(filename, 'w') as file:
            json.dump([data], file, indent=4)

# List objects in the S3 bucket with pagination
all_image_paths = []
continuation_token = None

while True:
    # Make the list_objects_v2 request with the continuation token
    list_objects_params = {'Bucket': s3_bucket_name, 'Prefix': 'WOMEN/'}

    if continuation_token:
        list_objects_params['ContinuationToken'] = continuation_token

    response = s3.list_objects_v2(**list_objects_params)

    # Check if there are Contents (objects) in the response
    if 'Contents' in response:
        for obj in response['Contents']:
            image_key = obj['Key']
            all_image_paths.append(image_key)

    # Check if there is a NextContinuationToken
    if 'NextContinuationToken' in response:
        continuation_token = response['NextContinuationToken']
    else:
        break


# Group images by product subfolder
image_groups = {}
for image_path in all_image_paths:
    product_subfolder = os.path.dirname(image_path)
    if product_subfolder not in image_groups:
        image_groups[product_subfolder] = []
    image_groups[product_subfolder].append(image_path)



# List to store the paths of the first image in each subfolder
first_images_list = []

# Iterate through the image groups and select the first image in each subfolder
for subfolder, image_paths in image_groups.items():
    if len(image_paths) > 0:
        first_image_path = image_paths[0]
        first_images_list.append(first_image_path)

image_path_url = []
base_url = "https://fashionimages05.s3.amazonaws.com/"


