FROM python:3.11-alpine3.16

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY app/requirements.txt /temp/requirements.txt
COPY app /app

WORKDIR /app
EXPOSE 8080

RUN apk add mariadb-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps gcc libc-dev linux-headers

RUN pip install --no-cache-dir -r /temp/requirements.txt
