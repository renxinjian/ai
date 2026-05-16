FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt fastapi uvicorn

COPY . .

RUN python3 scripts/init_db.py

EXPOSE 8080

CMD ["uvicorn", "mcp_servers.python.web_api:app", "--host", "0.0.0.0", "--port", "8080"]
