FROM python:3.11-slim

# Dépendances système
RUN apt-get update && apt-get install -y \
    sudo \
    ssh \
    gcc \
    docker.io \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
RUN pip install --no-cache-dir \
    ansible \
    docker \
    requests \
    flask \
    passlib

# Alias sécurité (si un module appelle "python")
RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /ansible

COPY . /ansible

CMD ["python3", "app.py"]

