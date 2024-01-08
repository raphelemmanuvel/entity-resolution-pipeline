# Stage 1: Build Entity Resolution Pipeline
FROM python:3.10.0-slim AS builder

MAINTAINER Emmanuvel Raphel <raphelemmanuvel@gmail.com>

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install --upgrade pip

# Install Poetry, a dependency manager for Python projects
RUN pip3 install poetry
RUN poetry config virtualenvs.create false

COPY . .

COPY poetry.lock pyproject.toml .

# Install the Python dependencies using Poetry
RUN poetry install

# Stage 2: Build Nginx image
FROM nginx:alpine

# Copy static files from the builder stage (Entity Resolution Pipeline)
COPY --from=builder /app/docs /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf
