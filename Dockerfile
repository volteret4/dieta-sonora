FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod -R a+rwX /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/tmp

EXPOSE 5001

ENTRYPOINT ["bash", "entrypoint.sh"]
CMD ["gunicorn", "-b", "0.0.0.0:5001", "--threads", "4", "--timeout", "600", "app:app"]
