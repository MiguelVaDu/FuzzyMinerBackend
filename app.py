from flask import Flask, jsonify
from flask_cors import CORS
from src.service import evaluate
from dotenv import load_dotenv
import os

# Opcional: precalentado del motor difuso para evitar latencia en el primer request
try:
    # Evita costo de compilación en la primera llamada
    from src.fuzzyminer import _get_cached_system  # tipo: ignore
except Exception:
    _get_cached_system = None  # type: ignore

load_dotenv()

app = Flask(__name__)
app.register_blueprint(evaluate)

# CORS: si no hay variable, permite todo
CORS(app, resources={r"/*": {'origins': os.getenv('CORS_TO_FRONTEND_CONECTION') or '*'}})

@app.get('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

# Precalentar al arrancar el proceso (funciona tanto con flask run como con gunicorn --preload)
if _get_cached_system is not None:
    try:
        _ = _get_cached_system()  # construye y cachea reglas/sistema
    except Exception:
        # No bloquear el arranque si el precalentado falla; la primera request lo reconstruirá
        pass

if __name__ == '__main__':
    # Solo para desarrollo local; en producción usar gunicorn (ver Dockerfile)
    port = int(os.getenv('PORT', '5000'))
    app.run(host='0.0.0.0', debug=True, port=port)
