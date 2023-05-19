FROM python:3.11-alpine3.16

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /temp/requirements.txt
COPY app /app

COPY nginx/conf.d /etc/nginx/conf.d

WORKDIR /app
EXPOSE 8000

RUN apk add mariadb-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps gcc libc-dev linux-headers
RUN apt-get update && \
    apt-get install -y shadow-utils


RUN pip install --no-cache-dir -r /temp/requirements.txt

RUN adduser --disabled-password app-user
RUN groupadd webusers
RUN chgrp -R webusers /app/media/
RUN adduser app-user webusers
RUN chmod -R 770 /app/media
RUN usermod -a -G webusers ubuntu

USER app-user
