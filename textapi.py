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

