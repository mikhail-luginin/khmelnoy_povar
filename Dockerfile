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

RUN pip install --no-cache-dir -r /temp/requirements.txt

RUN adduser --disabled-password app-user
RUN groupadd app-user-group
RUN adduser app-user app-user-group
RUN chgrp -R app-user-group /app/
RUN chmod -R 770 /app/media

USER app-user
