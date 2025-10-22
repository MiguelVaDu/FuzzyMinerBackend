# FuzzyMinerBackend

Backend Flask con lógica difusa (Mamdani) usando scikit-fuzzy para evaluar la competitividad de proveedores mineros.

El motor define funciones de pertenencia trapezoidales (0..5) y genera las 243 reglas desde una matriz EP embebida (27x9). No requiere archivos de reglas externos.

## Requisitos

- Python 3.10–3.12 recomendado
- Windows/macOS/Linux (en Windows se soporta Git Bash/Powershell)

Instala dependencias con requirements.txt: Flask, Flask-Cors, scikit-fuzzy, numpy, scipy, networkx.

## Configuración del entorno (virtualenv)

Ejecuta estos comandos en tu terminal (bash en Windows):

```bash
# 1) Crear y activar entorno virtual
python -m venv venv
source venv/Scripts/activate

# 2) Instalar dependencias
pip install -r requirements.txt
```

Si prefieres PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Variables de entorno

- `CORS_TO_FRONTEND_CONECTION` (opcional): origen permitido para CORS. Por defecto `*`.

Ejemplo (bash):

```bash
export CORS_TO_FRONTEND_CONECTION=http://localhost:5173
```

## Ejecutar el servidor

```bash
# Con el entorno virtual activado
python app.py
# El servidor escucha en http://localhost:5000
```

## API

- POST `/evaluate`
	- Body JSON: variables de entrada en 0..5, códigos o etiquetas
		- CIS, PRP, CCT, SF, SP
		- includeDetails (opcional): boolean (admite "true", "1", "on", "yes")
	- Respuesta (éxito):
		- `success`: boolean
		- `result`: objeto con al menos `{ label, crisp }`

### Formatos de entrada aceptados

1) Números 0..5 (int/float o string numérico)
2) Códigos (mayúsculas):
	 - CIS: BAJ, MED, ALT
	 - PRP: COS, COM, ECO
	 - CCT: DEF, BUE, EXC
	 - SF: INE, EST, SOL
	 - SP: DEF, BUE, EXC
3) Etiquetas (minúsculas, acentos opcionales):
	 - CIS: baja, media, alta
	 - PRP: costoso, competitivo, económico/economico
	 - CCT: deficiente, bueno, excelente
	 - SF: inestable, estable, solido/sólido
	 - SP: deficiente, bueno, excelente

### Ejemplos de request

Números 0..5:

```json
{
	"CIS": 3.2,
	"PRP": 2.8,
	"CCT": 4.0,
	"SF": 4.5,
	"SP": 2.9
}
```

Códigos:

```json
{
	"CIS": "MED",
	"PRP": "COS",
	"CCT": "BUE",
	"SF": "SOL",
	"SP": "DEF",
	"includeDetails": false
}
```

Etiquetas:

```json
{
	"CIS": "media",
	"PRP": "competitivo",
	"CCT": "bueno",
	"SF": "solido",
	"SP": "deficiente",
	"includeDetails": true
}
```

### Ejemplos de respuesta

Éxito (mínimo):

```json
{
	"success": true,
	"result": { "label": "Competitivo", "crisp": 3.2471 }
}
```

Error por parámetros faltantes (400):

```json
{
	"success": false,
	"error": "Parámetros faltantes",
	"missing": ["CIS", "PRP", "CCT", "SF", "SP"],
	"message": "Se requieren CIS, PRP, CCT, SF y SP (número 0..5, código o etiqueta)."
}
```

## Docker (opcional)

Hay un `Dockerfile` incluido. Construye y ejecuta:

```bash
docker build -t fuzzyminer-backend .
docker run --rm -p 5000:5000 fuzzyminer-backend
```

## Notas y resolución de problemas

- Versiones de Python: scikit-fuzzy depende de SciPy; si usas Python muy nuevo (p. ej., 3.13), puedes encontrar binarios no disponibles. Usa 3.10–3.12.
- CORS: si tu frontend falla por CORS, define `CORS_TO_FRONTEND_CONECTION` al origen correcto.
- Entradas inválidas: el backend devuelve 400 con mensaje de validación.
- Reglas: no edites archivos externos; la matriz EP está embebida en `src/fuzzyminer.py`.