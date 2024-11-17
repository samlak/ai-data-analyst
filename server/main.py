from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import io
import sys
import re
import matplotlib.pyplot as plt
from openai import AzureOpenAI
import pymongo
import uuid
from tabulate import tabulate 
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

app = FastAPI()

# Mount the "static" directory for serving image files
app.mount("/static", StaticFiles(directory="static"), name="static") 
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Setup
mongo_client = pymongo.MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DATABASE]
mongo_collection = mongo_db[MONGO_COLLECTION]

# Azure OpenAI Setup
client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT, 
    azure_deployment=AZURE_DEPLOYMENT,
    api_version=AZURE_API_VERSION,
    api_key=AZURE_API_KEY
)

# Data model for JSON response
class QueryResponse(BaseModel):
    table_output_verified: bool
    execution_result: str
    image_url: Optional[str] = None
    analysis: Optional[str] = None

# Utility functions
def generate_unique_code(length=8):
    code = str(uuid.uuid4()).replace('-', '')[:length]
    return code

def verify_table_output(generated_code):
    return "tabulate(" in generated_code and "print" in generated_code

def get_collection_schema():
    sample = mongo_collection.find_one()
    schema = {key: type(value).__name__ for key, value in sample.items()} if sample else {}
    return schema

def generate_code_for_query(question, schema, sample_data):
    """
    Generates Python code to query MongoDB based on a user's question.

    Args:
        question (str): User's question about the dataset.
        schema (dict): The schema of the MongoDB collection, mapping field names to data types.
        sample_data (list): Preview of MongoDB documents to help infer data structure.

    Returns:
        tuple: Generated Python code and the filename for any chart output.
    """
    
    output_filename = f"static/output_chart_{generate_unique_code()}.png"
    sample_data_preview = "\n".join([str(doc) for doc in sample_data[:3]])  # Display only first 3 documents
    schema_representation = "\n".join([f"{key}: {value}" for key, value in schema.items()])

    prompt = f"""
    You are a helpful Python data analysis assistant. Your task is to generate Python code for analyzing data stored in a MongoDB collection based on a user's question. 
    The dataset is represented as a MongoDB collection named `collection`. The user will provide a question, and your goal is to generate the correct code to answer it.

    ## Collection Schema:
    The MongoDB collection has the following schema:
    ```
    {schema_representation}
    ```

    ## Sample Data:
    Here is a preview of sample data from the MongoDB collection (first 3 documents):
    ```
    {sample_data_preview}
    ```

    ## Examples:

    **Example 1 (Table):**
    Question: "Show the top 5 most frequent values and their counts in the 'Category' field."  (If 'Category' doesn't exist, adapt to a similar categorical field from the schema)
    ```python
    from tabulate import tabulate
    data = collection.aggregate([
        {{"$group": {{"_id": "$Category", "count": {{"$sum": 1}}}}}},
        {{"$sort": {{"count": -1}}}},
        {{"$limit": 5}}
    ])
    data_list = [
        item for item in list(data)
        if isinstance(item["_id"], str)  # Ensure valid string values for categories
    ]
    headers = ["Category", "Count"]
    rows = [[item["_id"], item["count"]] for item in data_list]
    print(tabulate(rows, headers=headers, tablefmt="html"))
    ```

    **Example 2 (Chart):**
    Question: "Show the distribution of 'Price'." (If 'Price' doesn't exist, adapt to a similar numerical field from the schema)
    ```python
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    data = list(collection.find({""}, {{"Price": 1, "_id": 0}}))
    prices = [item["Price"] for item in data if isinstance(item.get("Price"), (int, float))]
    plt.hist(prices)
    plt.savefig("{output_filename}")
    plt.close()
    ```

    **Example 3 (Direct Print):**
    Question: "What is the average price?" (If 'Price' doesn't exist, adapt to a similar numerical field from the schema)
    ```python
    data = collection.find({""}, {{"Price": 1, "_id": 0}})
    prices = [
        float(item["Price"]) for item in data 
        if isinstance(item.get("Price"), (int, float))
    ]
    print(sum(prices) / len(prices))
    ```

    **Example 4 (Data Cleaning):**
    Question: "Find all records where the 'Date' field is after January 1, 2020."
    ```python
    from datetime import datetime
    data = collection.find({""}, {{"Date": 1, "_id": 0}})
    valid_records = [
        item for item in data 
        if isinstance(item.get("Date"), str) and datetime.strptime(item["Date"], "%Y-%m-%d") > datetime(2020, 1, 1)
    ]
    print(valid_records)
    ```

    ## Instructions:
    1. The MongoDB client has already been initiated, and the collection is loaded as `collection`. Use this collection to query the data. Do *not* include any code to initiate the MongoDB connection or collection.
    2. Only use the fields described in the schema. If a requested field is not in the schema, adapt the query to use an appropriate similar field in the schema or return an error message in the code.
    3. Handle data types carefully:
       - Validate field types using Python's `isinstance()` function before performing operations.
       - Convert field values to the correct type as specified in the schema (e.g., use `str()`, `float()`, or `datetime.strptime()`).
       - Skip or handle invalid values gracefully (e.g., log, replace, or ignore).
    4. If the answer requires cleaning or preprocessing the data:
       - Implement necessary data cleaning steps, such as filtering out invalid or null values.
       - Provide cleaned data for subsequent analysis.
    5. If a chart is the best way to answer the question:
       - Use `matplotlib` to generate the chart.
       - Save the chart as an image file with the name `{output_filename}`.
       - Use the `Agg` backend (`matplotlib.use('Agg')`) and call `plt.close()` after saving to prevent display.
    6. For tables, use the `tabulate` library and ensure proper headers are defined and output as an HTML table.
    7. Ensure your query is efficient and avoids fetching excessive data. Use aggregation pipelines or projections where applicable.
    8. Always prioritize generating correct and runnable Python code. Do not generate placeholders, pseudocode, or incomplete instructions.
    9. Provide only the Python code inside a ```python``` code block. Do not include any additional text or explanations.

    Now, generate code to answer the following question:
    "{question}"
    """

    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0
    )

    response_text = response.choices[0].message.content.strip()
    code_block = re.search(r"```python(.*?)```", response_text, re.DOTALL)
    generated_code = code_block.group(1).strip() if code_block else response_text
    return generated_code, output_filename

def execute_code(generated_code, image_path, collection):
    old_stdout = sys.stdout
    sys.stdout = output_capture = io.StringIO()
    generated_graph = False

    try:
        exec(generated_code, {'collection': collection, 'plt': plt, 'tabulate': tabulate})
        output = output_capture.getvalue()

        if os.path.exists(image_path):
            generated_graph = True
        else:
            image_path = ""

    except Exception as e:
        output = f"Error executing code: {e}"
    finally:
        sys.stdout = old_stdout

    return output, generated_graph, image_path if generated_graph else None

def analyze_output(question, output):
    prompt = f"""
    Based on the following question:
    '{question}'

    Here is the output of a Python code execution on a dataset:
    {output}

    Provide a very short analysis or summary that directly answers the question.
    """
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0
    )

    analysis = response.choices[0].message.content.strip()
    return analysis

@app.get("/query", response_model=QueryResponse)
async def query_mongodb(question: str = Query(..., description="The question about the MongoDB data")):
    try:
        sample_data = list(mongo_collection.find({}, {"_id": 0}).skip(20).limit(3)) # Skip the first 20 data because of insufficient information
        schema = get_collection_schema()

        generated_code, output_filename = generate_code_for_query(question, schema, sample_data)
        table_output_verified = verify_table_output(generated_code)

        print(generated_code)

        execution_result, generated_graph, image_url = execute_code(generated_code, output_filename, mongo_collection)

        if generated_graph:
            analysis = None
        else:
            analysis = analyze_output(question, execution_result)

        return QueryResponse(
            table_output_verified=table_output_verified,
            execution_result=execution_result,
            image_url=image_url.replace("static/", "/static/") if image_url else None,
            analysis=analysis
        )

    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))
