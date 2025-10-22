from flask import Blueprint, request, jsonify
import json
import time
from .fuzzyminer import evaluate_supplier

# Blueprint con nombre coherente al dominio
evaluate = Blueprint('evaluate', __name__)


def _parse_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in {"1", "true", "t", "yes", "y", "on"}
    if isinstance(v, (int, float)):
        return bool(v)
    return False


@evaluate.route('/evaluate', methods=['POST'])
def evaluate_handler():
    print('[evaluate] request received')
    try:
        # Obtener parámetros del request
        params = request.get_json(silent=True)
        # Fallback si el cliente no envía Content-Type: application/json
        if params is None and request.data:
            try:
                params = json.loads(request.data.decode('utf-8'))
            except Exception:
                params = None
        if params is None:
            return jsonify({
                "success": False,
                "error": "JSON inválido o ausente",
                "message": "Envía cuerpo JSON con CIS, PRP, CCT, SF y SP (número 0..5, código o etiqueta)."
            }), 400

        # Validar entradas requeridas
        required_keys = ['CIS', 'PRP', 'CCT', 'SF', 'SP']
        missing = [k for k in required_keys if k not in params]
        if missing:
            return jsonify({
                "success": False,
                "error": "Parámetros faltantes",
                "missing": missing,
                "message": "Se requieren CIS, PRP, CCT, SF y SP (número 0..5, código o etiqueta)."
            }), 400

        # Evaluar proveedor (pasar solo variables de entrada)
        eval_params = {k: params.get(k) for k in required_keys}
        include_details = _parse_bool(params.get('includeDetails', False))

        t0 = time.perf_counter()
        full = evaluate_supplier(eval_params, include_details=include_details)
        dt_ms = int((time.perf_counter() - t0) * 1000)
        print(f"[evaluate] dt={dt_ms}ms")
        # Respuesta mínima por defecto: solo label y crisp
        result = full if include_details else {"label": full.get("label"), "crisp": full.get("crisp")}

        return jsonify({"success": True, "result": result}), 200

    except ValueError as e:
        # Errores de validación de entradas (por ejemplo, códigos/etiquetas inválidos)
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Parámetros inválidos: usa número 0..5, código o etiqueta permitida."
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error interno del servidor al procesar la solicitud"
        }), 500


@evaluate.route('/evaluate', methods=['OPTIONS'])
def evaluate_options():
    # Respuesta vacía para preflight CORS
    return ('', 204)


@evaluate.route('/evaluate', methods=['GET'])
def evaluate_docs():
    return jsonify({
        "message": "Usa POST /evaluate con JSON {CIS, PRP, CCT, SF, SP} y opcional includeDetails",
        "example": {"CIS": "MED", "PRP": "COS", "CCT": "BUE", "SF": "SOL", "SP": "DEF"}
    }), 200


@evaluate.route('/ping', methods=['POST'])
def ping():
    return jsonify({"ok": True}), 200

