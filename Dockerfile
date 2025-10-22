FROM python:3.10.12

WORKDIR /app
COPY ./ /app

# Dependencias desde PyPI; crea directorio para config de Matplotlib (headless)
RUN pip install --no-cache-dir -r requirements.txt \
	&& mkdir -p /tmp/matplotlib

# Variables de entorno para Flask y Matplotlib
ENV FLASK_APP=app.py \
	MPLBACKEND=Agg \
	MPLCONFIGDIR=/tmp/matplotlib \
	PORT=5000

EXPOSE 5000

# Usa flask run simplificado pero respetando $PORT asignado por la plataforma
CMD ["sh", "-c", "exec flask run --host=0.0.0.0 --port ${PORT:-5000}"]