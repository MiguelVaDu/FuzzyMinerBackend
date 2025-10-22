FROM python:3.10.12

WORKDIR /app
COPY ./ /app

# Dependencias desde PyPI; crea directorio para config de Matplotlib (headless)
RUN pip install --no-cache-dir -r requirements.txt \
	&& mkdir -p /tmp/matplotlib

# Variables de entorno para Matplotlib y servidor
ENV MPLBACKEND=Agg \
	MPLCONFIGDIR=/tmp/matplotlib \
	PORT=5000 \
	WEB_CONCURRENCY=2 \
	GTHREADS=4 \
	GUNICORN_TIMEOUT=120

EXPOSE 5000

# Ejecuta con gunicorn en producción, con preload para calentar el modelo y mayor timeout
CMD ["sh", "-c", "exec gunicorn -w ${WEB_CONCURRENCY:-2} -k gthread --threads ${GTHREADS:-4} --timeout ${GUNICORN_TIMEOUT:-120} --preload -b 0.0.0.0:${PORT:-5000} app:app"]