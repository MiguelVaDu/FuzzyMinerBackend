FROM python:3.10.12

# Copia el código
COPY ./ /app
WORKDIR /app

# Instala dependencias del sistema necesarias para pip (git para instalar scikit-fuzzy desde GitHub)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends git \
	&& pip install --no-cache-dir -r requirements.txt \
	&& apt-get purge -y --auto-remove git \
	&& rm -rf /var/lib/apt/lists/*

# Puerto por defecto (sobrescribible por $PORT en runtime)
EXPOSE 5000

# Ejecuta con gunicorn en producción. Importante: usar shell para expandir $PORT.
# Variables ajustables: WEB_CONCURRENCY, GUNICORN_TIMEOUT y PORT (por la plataforma)
ENV PORT=5000
CMD ["sh", "-c", "exec gunicorn -w ${WEB_CONCURRENCY:-2} -k gthread -t ${GUNICORN_TIMEOUT:-120} -b 0.0.0.0:${PORT:-5000} app:app"]