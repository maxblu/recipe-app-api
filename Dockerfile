FROM  python:3.7-alpine
MAINTAINER dany


ENV PYTHONUNBUFFERED 1

COPY ./requeriments.txt /requeriments.txt
RUN pip install -r /requeriments.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

# securyty crete a seperate user
RUN adduser -D user
USER user