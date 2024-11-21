import os
from dotenv import load_dotenv

load_dotenv()

# Environment Variables
AZURE_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
AZURE_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")
AZURE_API_KEY = os.environ.get("AZURE_API_KEY") 
FRONTEND_URL = os.environ.get("FRONTEND_URL") 
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DATABASE = os.environ.get("MONGO_DB_NAME")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION_NAME")
