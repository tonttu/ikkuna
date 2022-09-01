FROM alpine:latest

WORKDIR /app
COPY requirements-docker.txt *.py ./
RUN apk add --no-cache python3 py3-pip py3-rpigpio py3-smbus \
    && pip install --no-cache-dir -r requirements-docker.txt
CMD ["python3", "ikkuna.py"]
