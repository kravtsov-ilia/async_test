FROM python:3.6.10-alpine3.11

COPY requirements.txt /opt/async_test/receiver/requirements.txt
ADD receiver.py /opt/async_test/receiver/

WORKDIR /opt/async_test/receiver/

RUN apk update \
    && apk add mpc1-dev \
    && apk add gcc libc-dev g++ \
    && pip install -r requirements.txt
