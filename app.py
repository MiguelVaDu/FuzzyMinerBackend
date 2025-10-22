from flask import Flask, jsonify
from flask_cors import CORS
from src.service import evaluate
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.register_blueprint(evaluate)

# Evita None en 'origins' (causa TypeError en flask-cors): usa '*' por defecto
# Lee ambas variantes del nombre de variable para evitar errores tipográficos
cors_origins = (
    os.getenv('CORS_TO_FRONTEND_CONNECTION')
    or os.getenv('CORS_TO_FRONTEND_CONECTION')
    or '*'
)
CORS(app, resources={r"/*": {'origins': cors_origins}})


@app.get('/')
def root():
    return jsonify({
        'status': 'ok',
        'service': 'FuzzyMinerBackend',
        'endpoints': {'POST /evaluate': 'Evalúa proveedor (CIS, PRP, CCT, SF, SP)'}
    }), 200


@app.get('/health')
def health():
    return jsonify({'status': 'healthy'}), 200


@app.before_first_request
def warmup():
    """Construye y cachea el sistema difuso en el arranque para evitar latencia en la primera evaluación."""
    try:
        from src.fuzzyminer import evaluate_supplier
        evaluate_supplier({'CIS': 3, 'PRP': 3, 'CCT': 3, 'SF': 3, 'SP': 3}, include_details=False)
        print('[warmup] Fuzzy system initialized')
    except Exception as e:
        print(f'[warmup] skipped: {e}')

if __name__ == '__main__':
    # En producción (Render) usa gunicorn: app:app y $PORT; este bloque es para local
    port = int(os.getenv('PORT', '5000'))
    app.run(host='0.0.0.0', debug=True, port=port)
