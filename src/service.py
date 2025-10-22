from flask import Blueprint, request, jsonify
from .fuzzyminer import evaluate_supplier

evaluate = Blueprint('evaluate', __name__)


@evaluate.route('/evaluate', methods=['POST'])
def evaluate_handler():
    try:
        params = request.get_json()
        if not params:
            return jsonify({
                "success": False,
                "error": "JSON inválido o ausente",
                "message": "Envía cuerpo JSON con CIS, PRP, CCT, SF y SP (número 0..5, código o etiqueta)."
            }), 400

        required_keys = ['CIS', 'PRP', 'CCT', 'SF', 'SP']
        missing = [k for k in required_keys if k not in params]
        if missing:
            return jsonify({
                "success": False,
                "error": "Parámetros faltantes",
                "missing": missing,
                "message": "Se requieren CIS, PRP, CCT, SF y SP (número 0..5, código o etiqueta)."
            }), 400

        eval_params = {k: params.get(k) for k in required_keys}
        include_details = bool(params.get('includeDetails', False))

        full = evaluate_supplier(eval_params, include_details=include_details)
        result = full if include_details else {"label": full.get("label"), "crisp": full.get("crisp")}

        return jsonify({"success": True, "result": result}), 200

    except ValueError as e:
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

