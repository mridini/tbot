FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 80
ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]
