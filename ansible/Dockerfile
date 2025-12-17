FROM python:3.11-slim

RUN apt update && apt install -y \
    ssh \
    sudo \
    gcc \
    python3-dev \
    libffi-dev \
    && pip install --no-cache-dir \
        ansible \
        docker \
        requests \
    && apt clean

WORKDIR /ansible

