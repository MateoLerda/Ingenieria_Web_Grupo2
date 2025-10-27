FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8
ENV PYTHONUTF8=1
WORKDIR /app

COPY . /app/

RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN mkdir -p /data

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]