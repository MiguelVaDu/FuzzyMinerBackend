from flask import Flask, jsonify
from flask_cors import CORS
from src.service import evaluate
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.register_blueprint(evaluate)

CORS(app, resources={r"/*": {'origins': os.getenv('CORS_TO_FRONTEND_CONECTION')}})

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=5000)
    print(f'Server running in ')