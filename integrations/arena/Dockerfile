# Build with --build-arg PYTHON_IMAGE=python@sha256:... after resolving a stable image.
ARG PYTHON_IMAGE=python:3.14-slim
FROM ${PYTHON_IMAGE}
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY omapet /app/omapet
USER 1000:1000
CMD ["python", "-m", "omapet.arena", "--host", "127.0.0.1", "--port", "18765", "--state", "/state/arena.json", "--invite-file", "/run/secrets/invite", "--trust-cloudflare"]
