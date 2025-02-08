FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8001", "app:app", "--workers=6"]
