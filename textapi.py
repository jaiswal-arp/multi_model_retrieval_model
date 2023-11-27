import os
import boto3
import base64
import openai
import requests
import json
import time

OPENAI_API_TOKEN = "open_api_key"
os.environ["OPENAI_API_KEY"] = OPENAI_API_TOKEN


