FROM python:3.10.0-slim
MAINTAINER Emmanuvel Raphel <emmanuvel@thinkdataworks.com>

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install --upgrade pip

RUN pip3 install poetry
RUN poetry config virtualenvs.create false

ADD . /app/

COPY poetry.lock pyproject.toml .

RUN poetry install
