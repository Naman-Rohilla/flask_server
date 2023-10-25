FROM python:3.10

RUN apt-get update && apt-get install -y tesseract-ocr

# Install your Flask application dependencies here
COPY requirements.txt

RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

CMD ["python", "server.py"]
