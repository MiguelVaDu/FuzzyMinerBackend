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
- `PORT` (interna de PaaS): algunas plataformas la asignan automáticamente. El contenedor escucha en `0.0.0.0:$PORT`.

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

## Despliegue en Render

Puedes desplegar este backend en Render como Web Service con Docker.

1) Conecta tu repo a Render y crea un nuevo Web Service.
2) Environment: Docker (Render usará el `Dockerfile`).
3) Health Check Path: pon `/health` para que Render valide el contenedor.
4) Variables de entorno recomendadas:
	- `CORS_TO_FRONTEND_CONECTION`: origen permitido (por ejemplo, `https://tu-frontend.com`).
	- `WEB_CONCURRENCY`: número de workers Gunicorn (por defecto 2).
	- `GTHREADS`: threads por worker (por defecto 4).
	- `GUNICORN_TIMEOUT`: timeout de request en Gunicorn (por defecto 120 s).
	- Opcional: `OMP_NUM_THREADS=1` para limitar hilos nativos de NumPy/SciPy en CPUs pequeñas.

El contenedor arranca con Gunicorn usando `--preload`, lo que precalienta el motor difuso en el arranque para evitar latencia en la primera petición. Render establece `PORT` automáticamente; el contenedor ya escucha en `0.0.0.0:$PORT`.

### Notas de tiempo de respuesta y timeouts

- Tras el arranque, las peticiones a `/evaluate` deben ser rápidas. Si la primera petición encuentra el servicio “frío”, el precalentado ya se hizo al iniciar Gunicorn.
- Si tu instancia entra en reposo y Render la despierta, el primer request volverá a ser atendido tras el arranque, pero el modelo ya se precarga antes del primer request.
- Si ves “timeout” del lado de Render (límite del proxy), incrementa `GUNICORN_TIMEOUT` y asegúrate de que el cómputo por request no excede el límite del proxy de Render. Si necesitas operaciones de larga duración, considera un job en background con 202 + polling.

### Prueba rápida en Render

1) Verifica `GET /health` (debe responder 200 con `{ "status": "healthy" }`).
2) Envía un `POST /evaluate` con un JSON válido (ver ejemplos arriba). Deberías obtener `{ success: true, result: { label, crisp } }`.


### Notas de compatibilidad de dependencias

- Para evitar depender de `git` en la build, este proyecto usa `scikit-fuzzy==0.4.2` desde PyPI con:
	- `numpy==1.23.5`, `scipy==1.10.1`, `networkx==2.8.8`.
- Si necesitas `numpy>=2`, usa la versión de `scikit-fuzzy` desde GitHub y añade `git` en la imagen. En ese caso, cambia en `requirements.txt` a:
	- `numpy>=2`, `scipy>=1.14`, `networkx>=3`, y `scikit-fuzzy @ git+https://github.com/scikit-fuzzy/scikit-fuzzy.git`.
	- Ajusta el Dockerfile para instalar `git` antes de `pip install`.

## Notas y resolución de problemas

- Versiones de Python: scikit-fuzzy depende de SciPy; si usas Python muy nuevo (p. ej., 3.13), puedes encontrar binarios no disponibles. Usa 3.10–3.12.
- CORS: si tu frontend falla por CORS, define `CORS_TO_FRONTEND_CONECTION` al origen correcto.
- Entradas inválidas: el backend devuelve 400 con mensaje de validación.
- Reglas: no edites archivos externos; la matriz EP está embebida en `src/fuzzyminer.py`.