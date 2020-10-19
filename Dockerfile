FROM  python:3.7-alpine
MAINTAINER dany


ENV PYTHONUNBUFFERED 1

COPY ./requeriments.txt /requeriments.txt
RUN apk add --update --no-cache postgresql-client
Run apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requeriments.txt
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

# securyty crete a seperate user
RUN adduser -D user
USER user