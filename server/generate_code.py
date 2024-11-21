import re

def generate_code_for_query(
    question, 
    schema, 
    sample_data, 
    client, 
    generate_unique_code, 
    AZURE_DEPLOYMENT
):
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
    sample_data_preview = "\n".join([str(doc) for doc in sample_data[:3]])
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
