FROM python:3.13-slim

LABEL authors="vbaho"

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

EXPOSE 8001

CMD ["sh", "-c", "\
    python3 manage.py migrate --noinput && \
    python3 manage.py collectstatic --noinput && \
    python3 manage.py add_regions && \
    python3 manage.py add_products && \
    python3 manage.py runserver 0.0.0.0:8001"]
