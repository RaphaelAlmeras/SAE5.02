FROM python:3.11-slim

RUN apt update && apt install -y \
    ssh \
    sudo \
    gcc \
    docker.io \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    python3-dev \
    libffi-dev \
    && pip install --no-cache-dir \
        ansible \
        docker \
        requests \
	flask \
    && apt clean

WORKDIR /ansible

