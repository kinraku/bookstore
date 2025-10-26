FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y default-mysql-client libmariadb-dev-compat gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN mkdir -p static/uploads/books

EXPOSE 5000

CMD ["python", "app.py"]
