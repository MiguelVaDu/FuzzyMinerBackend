"""
Motor de lógica difusa Mamdani para evaluar proveedores mineros con skfuzzy.control.
Usa funciones de pertenencia trapezoidales y genera las 243 reglas directamente
desde una matriz EP embebida (27x9). Acepta entradas 0..5, códigos o etiquetas,
y devuelve el valor crisp y la etiqueta de EP resultante.

Entradas (0..5) o etiquetas/códigos:
- CIS: Baja (BAJ), Media (MED), Alta (ALT)
- PRP: costos/Costoso (COS), competitivo (COM), económico (ECO)
- CCT: deficiente (DEF), bueno (BUE), excelente (EXC)
- SF: inestable (INE), estable (EST), solido (SOL)
- SP: deficiente (DEF), bueno (BUE), excelente (EXC)

Salida EP (0..5):
- No competitivo, Poco competitivo, Competitivo, Muy competitivo

Funciones de pertenencia trapezoidales tal como en el PDF. Las 243 reglas
se generan directamente desde una matriz EP embebida (27x9) que cubre todos los casos.
"""

from __future__ import annotations

from typing import Dict, List, Any, Tuple, Optional
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
 

# ------------ Definición de variables lingüísticas ------------

# Parámetros de MF según especificación (escala 0..5)
MF_PARAMS: Dict[str, Dict[str, List[float]]] = {
    'CIS': {
        'baja':      [0.0, 0.0, 2.5, 3.0],
        'media':     [2.5, 3.0, 3.8, 3.9],
        'alta':      [3.8, 4.3, 5.0, 5.0],
    },
    'PRP': {
        'costoso':       [0.0, 0.0, 2.6, 2.7],  # "Costoso" (COS)
        'competitivo':   [2.6, 3.0, 3.7, 3.8],
        'económico':     [3.8, 4.0, 5.0, 5.0],
    },
    'CCT': {
        'deficiente':    [0.0, 0.0, 2.5, 3.0],
        'bueno':         [2.8, 3.0, 3.9, 4.1],
        'excelente':     [3.9, 4.0, 5.0, 5.0],
    },
    'SF': {
        'inestable':     [0.0, 0.0, 2.5, 3.0],
        'estable':       [2.8, 3.0, 3.9, 4.1],
        'solido':        [3.9, 4.0, 5.0, 5.0],
    },
    'SP': {
        'deficiente':    [0.0, 0.0, 2.5, 2.9],
        'bueno':         [2.7, 3.0, 3.9, 4.0],
        'excelente':     [3.9, 4.0, 5.0, 5.0],
    },
    'EP': {
        'No competitivo':     [0.0, 0.0, 0.8, 1.3],
        'Poco competitivo':   [0.9, 1.4, 2.2, 2.7],
        'Competitivo':        [2.3, 2.8, 3.6, 4.1],
        'Muy competitivo':    [3.7, 4.2, 5.0, 5.0],
    },
}

# Construcción de universo para todas las variables (0..5)
UNIVERSE = np.arange(0.0, 5.01, 0.01)
 
# Antecedentes/Consecuente con MFs trapezoidales
def build_antecedent(name: str) -> ctrl.Antecedent:
    ant = ctrl.Antecedent(UNIVERSE, name)
    for label, p in MF_PARAMS[name].items():
        ant[label] = fuzz.trapmf(ant.universe, p)
    return ant

def build_consequent(name: str) -> ctrl.Consequent:
    con = ctrl.Consequent(UNIVERSE, name)
    for label, p in MF_PARAMS[name].items():
        con[label] = fuzz.trapmf(con.universe, p)
    return con



# ------------ Reglas ------------

# Normalización de etiquetas (acepta códigos del documento y variantes sin tilde)
_LABEL_NORMALIZER: Dict[str, Dict[str, str]] = {
    'CIS': {
        'BAJ': 'baja', 'MED': 'media', 'ALT': 'alta',
        'baja': 'baja', 'media': 'media', 'alta': 'alta',
    },
    'PRP': {
        'COS': 'costoso', 'COM': 'competitivo', 'ECO': 'económico',
        'costoso': 'costoso', 'competitivo': 'competitivo',
        'economico': 'económico', 'económico': 'económico',
    },
    'CCT': {
        'DEF': 'deficiente', 'BUE': 'bueno', 'EXC': 'excelente',
        'deficiente': 'deficiente', 'bueno': 'bueno', 'excelente': 'excelente',
    },
    'SF': {
        'INE': 'inestable', 'EST': 'estable', 'SOL': 'solido',
        'inestable': 'inestable', 'estable': 'estable', 'solido': 'solido', 'sólido': 'solido',
    },
    'SP': {
        'DEF': 'deficiente', 'BUE': 'bueno', 'EXC': 'excelente',
        'deficiente': 'deficiente', 'bueno': 'bueno', 'excelente': 'excelente',
    },
    'EP': {
        'NOC': 'No competitivo', 'POC': 'Poco competitivo', 'COM': 'Competitivo', 'MUY': 'Muy competitivo',
        'No competitivo': 'No competitivo', 'Poco competitivo': 'Poco competitivo',
        'Competitivo': 'Competitivo', 'Muy competitivo': 'Muy competitivo',
        # Acepta también minúsculas
        'no competitivo': 'No competitivo', 'poco competitivo': 'Poco competitivo',
        'competitivo': 'Competitivo', 'muy competitivo': 'Muy competitivo',
    }
}


def _norm_label(var: str, value: str) -> str:
    if value in MF_PARAMS.get(var, {}):
        return value
    return _LABEL_NORMALIZER.get(var, {}).get(value, value)

 

# ----- Matriz EP embebida (27x9) para fallback -----
_EP_CODE_TO_LABEL = {
    'NOC': 'No competitivo',
    'POC': 'Poco competitivo',
    'COM': 'Competitivo',
    'MUY': 'Muy competitivo',
}

_CIS_ORDER = ['baja', 'media', 'alta']
_PRP_ORDER = ['costoso', 'competitivo', 'económico']
_CCT_ORDER = ['deficiente', 'bueno', 'excelente']
_SF_ORDER  = ['inestable', 'estable', 'solido']
_SP_ORDER  = ['deficiente', 'bueno', 'excelente']

_EP_MATRIX_CODES = [
    ['NOC','NOC','NOC','NOC','NOC','POC','NOC','NOC','POC'],
    ['NOC','NOC','POC','NOC','POC','POC','NOC','POC','POC'],
    ['NOC','POC','POC','POC','POC','POC','POC','POC','COM'],
    ['NOC','NOC','POC','NOC','POC','POC','NOC','POC','POC'],
    ['NOC','POC','POC','POC','POC','POC','POC','POC','COM'],
    ['POC','POC','COM','POC','POC','COM','POC','COM','COM'],
    ['POC','POC','POC','POC','POC','COM','POC','POC','COM'],
    ['POC','POC','COM','POC','COM','COM','POC','COM','COM'],
    ['POC','COM','COM','COM','COM','COM','COM','COM','MUY'],
    ['NOC','NOC','POC','NOC','POC','POC','NOC','POC','POC'],
    ['NOC','POC','POC','POC','POC','POC','POC','POC','COM'],
    ['POC','POC','COM','POC','POC','COM','POC','COM','COM'],
    ['POC','POC','POC','POC','POC','COM','POC','POC','COM'],
    ['POC','POC','COM','POC','COM','COM','POC','COM','COM'],
    ['POC','COM','COM','COM','COM','COM','COM','COM','MUY'],
    ['POC','POC','COM','POC','COM','COM','POC','COM','COM'],
    ['POC','COM','COM','COM','COM','COM','COM','COM','MUY'],
    ['COM','COM','MUY','COM','COM','MUY','COM','MUY','MUY'],
    ['POC','POC','POC','POC','POC','COM','POC','POC','COM'],
    ['POC','POC','COM','POC','COM','COM','POC','COM','COM'],
    ['POC','COM','COM','COM','COM','COM','COM','COM','MUY'],
    ['POC','POC','COM','POC','COM','COM','POC','COM','COM'],
    ['POC','COM','COM','COM','COM','COM','COM','COM','MUY'],
    ['COM','COM','MUY','COM','COM','MUY','COM','MUY','MUY'],
    ['COM','COM','COM','COM','COM','MUY','COM','COM','MUY'],
    ['COM','COM','MUY','COM','MUY','MUY','COM','MUY','MUY'],
    ['COM','MUY','MUY','MUY','MUY','MUY','MUY','MUY','MUY'],
]

def _build_rules_from_matrix_ctrl(CIS, PRP, CCT, SF, SP, EP) -> List[ctrl.Rule]:
    rules_ctrl: List[ctrl.Rule] = []
    row_idx = 0
    for cis in _CIS_ORDER:
        for prp in _PRP_ORDER:
            for cct in _CCT_ORDER:
                row = _EP_MATRIX_CODES[row_idx]
                col_idx = 0
                for sf in _SF_ORDER:
                    for sp in _SP_ORDER:
                        code = row[col_idx]
                        then_label = _EP_CODE_TO_LABEL[code]
                        antecedent = (
                            CIS[cis] & PRP[prp] & CCT[cct] & SF[sf] & SP[sp]
                        )
                        rules_ctrl.append(ctrl.Rule(antecedent, EP[then_label]))
                        col_idx += 1
                row_idx += 1
    return rules_ctrl


# ------------ Evaluación y utilidades ------------

def _label_to_crisp(var: str, label: str) -> float:
    """Convierte una etiqueta válida en un valor representativo (centro del núcleo del trapecio).
    Usa el promedio de los puntos b y c de la trapmf [a,b,c,d]."""
    p = MF_PARAMS[var][label]
    b, c = float(p[1]), float(p[2])
    return (b + c) / 2.0

def _parse_input_value(var: str, v: Any) -> float:
    """Acepta números (0..5), strings numéricos, códigos (BAJ/COS/...) o etiquetas completas.
    Devuelve un float en 0..5."""
    # 1) Números directos
    if isinstance(v, (int, float)):
        return float(v)
    # 2) Strings numéricos
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            pass
        # 3) Códigos o etiquetas
        norm = _norm_label(var, v)
        if norm in MF_PARAMS.get(var, {}):
            return _label_to_crisp(var, norm)
        raise ValueError(f"Valor inválido para {var}: {v}")
    # 4) Otros tipos no soportados
    raise ValueError(f"Tipo de valor inválido para {var}: {type(v).__name__}")

 

_CACHED_CS: Optional[Tuple[str, ctrl.ControlSystem]] = None  # (key, system)

def _get_cached_system() -> ctrl.ControlSystem:
    global _CACHED_CS
    key = "matrix"
    if _CACHED_CS is None or _CACHED_CS[0] != key:
        CIS = build_antecedent('CIS')
        PRP = build_antecedent('PRP')
        CCT = build_antecedent('CCT')
        SF  = build_antecedent('SF')
        SP  = build_antecedent('SP')
        EP  = build_consequent('EP')
        rules_ctrl = _build_rules_from_matrix_ctrl(CIS, PRP, CCT, SF, SP, EP)
        system = ctrl.ControlSystem(rules_ctrl)
        _CACHED_CS = (key, system)
    return _CACHED_CS[1]


def best_ep_label(crisp_value: float) -> str:
    """Devuelve la etiqueta de EP con mayor pertenencia en el valor crisp."""
    # Evalúa el valor crisp contra las MF de salida usando skfuzzy
    ep_params = MF_PARAMS['EP']
    label, _ = max(
        (
            (lbl, float(fuzz.trapmf(np.array([crisp_value]), p)[0]))
            for lbl, p in ep_params.items()
        ),
        key=lambda t: t[1]
    )
    return label


def evaluate_supplier(params: Dict[str, Any], include_details: bool = True) -> Dict[str, Any]:
    """
    Evalúa un proveedor.
    params: {CIS, PRP, CCT, SF, SP} en escala 0..5 (float o int).
    Retorna: { crisp, label, details }
    """
    # Normaliza entradas a float: acepta 0..5, strings numéricos, códigos (BAJ/COS/DEF/...) o etiquetas
    inputs = {
        'CIS': _parse_input_value('CIS', params.get('CIS', 0.0)),
        'PRP': _parse_input_value('PRP', params.get('PRP', 0.0)),
        'CCT': _parse_input_value('CCT', params.get('CCT', 0.0)),
        'SF':  _parse_input_value('SF',  params.get('SF',  0.0)),
        'SP':  _parse_input_value('SP',  params.get('SP',  0.0)),
    }

    # Sistema Mamdani con skfuzzy.control
    system = _get_cached_system()
    sim = ctrl.ControlSystemSimulation(system)
    sim.input['CIS'] = inputs['CIS']
    sim.input['PRP'] = inputs['PRP']
    sim.input['CCT'] = inputs['CCT']
    sim.input['SF']  = inputs['SF']
    sim.input['SP']  = inputs['SP']
    sim.compute()
    crisp = float(sim.output['EP'])
    label = best_ep_label(crisp)

    result = {
        'inputs': inputs,
        'crisp': round(crisp, 4),
        'label': label,
    }
    return result


# Alias para compatibilidad si alguien importaba inference_engine
def inference_engine(params: Dict[str, Any]):
    return evaluate_supplier(params)
