import sys
import io
import matplotlib.pyplot as plt
from tabulate import tabulate 
import os

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
