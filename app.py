from flask import Flask, jsonify, request
from flask_cors import CORS
from src.service import evaluate
from flask import Flask, jsonify
from flask_cors import CORS
from src.service import evaluate
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.register_blueprint(evaluate)

# CORS simple, como en tu ejemplo; si no hay variable, permite todo
CORS(app, resources={r"/*": {'origins': os.getenv('CORS_TO_FRONTEND_CONECTION') or '*'}})

@app.get('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Local: permite sobreescribir el puerto por PORT o usar 5000
    port = int(os.getenv('PORT', '5000'))
    app.run(host='0.0.0.0', debug=True, port=port)
    # Log muy ligero para diagnosticar problemas de POST/OPTIONS en despliegue
    try:
        print(f"[req] {request.method} {request.path} from {request.headers.get('Origin')}")
    except Exception:
        pass

if __name__ == '__main__':
    # En producción (Render) usa gunicorn: app:app y $PORT; este bloque es para local
    port = int(os.getenv('PORT', '5000'))
    app.run(host='0.0.0.0', debug=True, port=port)
