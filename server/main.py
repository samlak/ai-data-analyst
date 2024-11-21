from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from openai import AzureOpenAI
import pymongo
from constant import *
from utils import generate_unique_code, verify_table_output, get_collection_schema 
from generate_code import generate_code_for_query
from execute_code import execute_code
from analyze_output import analyze_output

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

@app.get("/query", response_model=QueryResponse)
async def query_mongodb(question: str = Query(..., description="The question about the MongoDB data")):
    try:
        sample_data = list(mongo_collection.find({}, {"_id": 0}).skip(20).limit(3)) # Skip the first 20 data because of insufficient information
        schema = get_collection_schema(mongo_collection)

        generated_code, output_filename = generate_code_for_query(
            question, 
            schema, 
            sample_data,
            client,
            generate_unique_code,
            AZURE_DEPLOYMENT
        )
        table_output_verified = verify_table_output(generated_code)

        print(generated_code)

        execution_result, generated_graph, image_url = execute_code(generated_code, output_filename, mongo_collection)

        if generated_graph:
            analysis = None
        else:
            analysis = analyze_output(question, execution_result, client, AZURE_DEPLOYMENT)

        return QueryResponse(
            table_output_verified=table_output_verified,
            execution_result=execution_result,
            image_url=image_url.replace("static/", "/static/") if image_url else None,
            analysis=analysis
        )

    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))
