import uuid

# Utility functions
def generate_unique_code(length=8):
    code = str(uuid.uuid4()).replace('-', '')[:length]
    return code

def verify_table_output(generated_code):
    return "tabulate(" in generated_code and "print" in generated_code

def get_collection_schema(mongo_collection):
    sample = mongo_collection.find_one()
    schema = {key: type(value).__name__ for key, value in sample.items()} if sample else {}
    return schema

