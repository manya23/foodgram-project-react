FROM python:3.7-slim

WORKDIR /app

COPY ./backend/api_foodgram .

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2==2.8.6 \
    && pip install django-cors-headers \
    && apt install -y python3-pip python3-cffi \
    python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "api_foodgram.wsgi:application", "--bind", "0:8000" ]