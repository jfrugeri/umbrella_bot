from flask import Flask, request
from datetime import datetime
import subprocess
import sys
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

ALLOWED_IPS = os.getenv('ALLOWED_IPS', '').split(',')

def log_response(message, status_code):
    """Helper function to log responses with timestamp."""
    timenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{timenow}] - {message}", status_code

def execute_script(script_name):
    """Helper function to execute a script and log the output."""
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True
        )
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        if result.returncode != 0:
            return log_response(f"Error executing {script_name}: {result.stderr}", 500)

        return log_response(f"Successfully executed {script_name}", 200)
    except Exception as e:
        return log_response(f"Error when executing {script_name}: {str(e)}", 500)

@app.route('/', methods=['GET'])
def execute_main():
    client_ip = request.remote_addr
    param = request.args.get('param')  # Get the 'param' parameter
    
    # Check if the IP is in the allowed list
    if client_ip not in ALLOWED_IPS:
        return log_response("Forbidden", 403)

    if param == 'main':
        return execute_script('main.py')

    return log_response("Invalid parameter. Not Found", 404)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)