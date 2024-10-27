import os
from dotenv import load_dotenv

def get_api_key(api_key_name):
    load_dotenv()
    return os.getenv(api_key_name)