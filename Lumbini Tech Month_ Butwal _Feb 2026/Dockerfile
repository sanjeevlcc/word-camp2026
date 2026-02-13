
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates ./templates

ENV RUN_MODE="Docker"
ENV APP_SECRET="change-me"

EXPOSE 5000
CMD ["gunicorn","-w","1","-b","0.0.0.0:5000","app:app"]
