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
import uuid
from tabulate import tabulate 
import os
from dotenv import load_dotenv

load_dotenv()

# Loading environment variables
AZURE_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
AZURE_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")
AZURE_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY") 
FRONTEND_URL = os.environ.get("FRONTEND_URL") 

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

# Azure OpenAI setup
client = AzureOpenAI(
    azure_endpoint = AZURE_ENDPOINT, 
    azure_deployment = AZURE_DEPLOYMENT,
    api_version = AZURE_API_VERSION,
    api_key = AZURE_API_KEY
)

# Load CSV into a DataFrame once 
df = pd.read_csv("dataset/dataset_purchase_nano.csv")

# Data model for JSON response
class QueryResponse(BaseModel):
    table_output_verified: bool
    execution_result: str
    image_url: Optional[str] = None
    analysis: Optional[str] = None

def generate_unique_code(length=8):
    code = str(uuid.uuid4()).replace('-', '')[:length]
    return code

def verify_table_output(generated_code):
    if "tabulate(" in generated_code and "print" in generated_code: 
        return True
    else:
        return False 

def generate_code_for_query(question, dataframe):
    columns = ', '.join(dataframe.columns)
    data_preview = dataframe.head().to_string(index=False)

    output_filename = f"static/output_chart_{generate_unique_code()}.png"

    prompt = f"""
    You are a helpful Python data analysis assistant. Given the following dataset information and a user's question, generate Python code that answers the question using pandas and matplotlib/tabulate.

    Dataset Columns: {columns}
    Dataset Preview:
    ```
    {data_preview}
    ```

    ## Examples:

    **Example 1 (Table):**
    Question: "Show the top 5 most frequent values and their counts in the 'Category' column."  (If 'Category' doesn't exist, adapt to a similar categorical column)
    ```python
    from tabulate import tabulate
    print(tabulate(df['Category'].value_counts().head().to_frame(), headers="keys", tablefmt="html"))
    ```

    **Example 2 (Chart):**
    Question: "Show the distribution of 'Price'." (If 'Price' doesn't exist, adapt to a similar numerical column)
    ```python
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.hist(df['Price'])
    plt.savefig('{output_filename}')
    plt.close()
    ```

    **Example 3 (Direct Print):**
    Question: "What is the average price?" (If 'Price' doesn't exist, adapt to a similar numerical column)
    ```python
    print(df['Price'].mean())
    ```

    Now, answer the following question: "{question}"

    Instructions:
    1. The dataset is already loaded into a pandas DataFrame named `df`.  Do *not* include any code to read or import the dataset.
    2. If the answer is best represented as a table, use the `tabulate` library (which you must import) to format the output as a Markdown table and print the result. Make sure to use the 'html' format for the table.  For example, `print(tabulate(your_table_data, headers="keys", tablefmt="html"))`.
    3. If a chart is a suitable or more insightful way to answer the question, generate the chart using matplotlib, save it as '{output_filename}', and follow the plotting instructions given previously. Include necessary imports, use the `Agg` backend (`matplotlib.use('Agg')`), and call `plt.close()` after saving to prevent display. Do not include `plt.show()`.
    4. For other answers, directly print the result.
    5. Prioritize clarity and conciseness in the generated code.  Do not include any additional explanations or comments unless absolutely necessary.
    6. Ensure your code runs without errors given the provided data preview.
    7. Do not generate a table unless it is the most effective and concise way to present the answer.  Prioritize other output formats (charts or direct printing of results) if they are more suitable.

    Provide only the Python code within a ```python code block.  Do not include any other text or explanations.
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


def execute_code(generated_code, image_path, dataframe):
    old_stdout = sys.stdout
    sys.stdout = output_capture = io.StringIO()
    generated_graph = False

    try:
        exec(generated_code, {'df': dataframe, 'plt': plt, 'tabulate': tabulate})
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
async def query_csv(question: str = Query(..., description="The question about the CSV data")):
    try:
        generated_code, output_filename = generate_code_for_query(question, df)
        table_output_verified = verify_table_output(generated_code)

        print(generated_code)
        print(table_output_verified)
        

        execution_result, generated_graph, image_url = execute_code(generated_code, output_filename, df)

        if generated_graph:
            analysis = None
        else:
            analysis = analyze_output(question, execution_result)

        return QueryResponse(
            table_output_verified = table_output_verified,
            execution_result=execution_result,
            image_url=image_url.replace("static/", "/static/") if image_url else None,
            analysis=analysis
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))