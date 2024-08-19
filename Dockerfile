FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install docker
CMD ["python", "/app/main.py"]
