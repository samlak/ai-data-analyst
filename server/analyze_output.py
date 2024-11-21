
def analyze_output(question, output, client, AZURE_DEPLOYMENT):
    prompt = f"""
    Based on the following question:
    '{question}'

    Here is the output of a Python code execution on a dataset:
    {output}

    Provide a very short analysis or summary that directly answers the question.
    """
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT, 
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0
    )

    analysis = response.choices[0].message.content.strip()
    return analysis