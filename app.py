from flask import Flask, request
from datetime import datetime
import subprocess, sys, os
from dotenv import load_dotenv

# Carrega o arquivo .env
load_dotenv()

app = Flask(__name__)

# Obtém a lista de IPs permitidos do .env e converte em lista
ALLOWED_IPS = os.getenv('ALLOWED_IPS', '').split(',')

def log_response(message, status_code):
    """Helper function to log responses with timestamp."""
    timenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{timenow}] - {message}", status_code

@app.route('/main', methods=['GET'])
def execute_main():
    client_ip = request.remote_addr
    param = request.args.get('param')  # Obtém o parâmetro 'param'
    
    # Verifica se o IP está na lista permitida
    if client_ip not in ALLOWED_IPS:
        return log_response("Forbidden", 403)

    if param == '/':
        try:
            result = subprocess.run(
                [sys.executable, 'main.py'],
                cwd=os.path.dirname(__file__),
                capture_output=True,
                text=True
            )
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)

            if result.returncode != 0:
                return log_response(f"Error executing main.py: {result.stderr}", 500)

            return log_response("Successfully Executed main.py", 200)
        except Exception as e:
            return log_response(f"Error when executing: {str(e)}", 500)

    # Caso o parâmetro não seja `/` ou vazio
    return log_response("Invalid parameter. Not Found", 404)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
