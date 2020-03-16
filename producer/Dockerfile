FROM python:3.6.10-alpine3.11

COPY requirements.txt /opt/async_test/producer/requirements.txt
ADD producer.py /opt/async_test/producer/

WORKDIR /opt/async_test/producer/

RUN apk update \
    && apk add mpc1-dev \
    && apk add gcc libc-dev g++ \
    && pip install -r requirements.txt
