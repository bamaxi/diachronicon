FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY app app
COPY migrations migrations
COPY config.py runserver.py ./
COPY diachronicon.db diachronicon.db


ENV FLASK_APP runserver.py

EXPOSE 5001

CMD ["flask", "run", "--host", "0.0.0.0", "-p", "5001"]

