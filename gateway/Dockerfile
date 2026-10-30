FROM python:3.10.0-slim
WORKDIR /gateway
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ingestor.py ingestor.py
CMD ["python3", "-u", "ingestor.py"]
