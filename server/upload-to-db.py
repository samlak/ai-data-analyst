import pandas as pd
from pymongo import MongoClient
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# MongoDB connection details
MONGO_URI = os.getenv("MONGO_URI") 
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME") 
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME") 


def upload_csv_to_mongodb(csv_file_path):
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        collection = db[MONGO_COLLECTION_NAME]

        # Load CSV file into a DataFrame
        print(f"Loading CSV file: {csv_file_path}")
        df = pd.read_csv(csv_file_path)

        # Convert DataFrame to a list of dictionaries
        records = df.to_dict(orient="records")

        # Insert records into MongoDB collection
        print(f"Inserting {len(records)} records into MongoDB collection '{MONGO_COLLECTION_NAME}'...")
        collection.insert_many(records)

        print("Upload successful!")
    except Exception as e:
        print(f"Error uploading CSV to MongoDB: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    # Replace with the path to your CSV file
    csv_file_path = "dataset/dataset_purchase_nano.csv"
    upload_csv_to_mongodb(csv_file_path)
