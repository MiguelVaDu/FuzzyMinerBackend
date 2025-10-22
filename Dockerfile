FROM python:3.10.12

COPY ./ /app
WORKDIR /app


RUN pip install -r requirements.txt


EXPOSE 5000

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]