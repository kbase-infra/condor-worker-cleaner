FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
RUN chmod +x /app/main.sh
#CMD ["python", "/app/main.py"]
CMD ["/app/run.sh"]