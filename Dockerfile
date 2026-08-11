FROM python:3.12-alpine

WORKDIR /app
COPY app.py index.html ./

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=4)"

USER 10001
CMD ["python", "app.py"]
