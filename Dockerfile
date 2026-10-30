# syntax=docker/dockerfile:1
FROM python:3.13

WORKDIR /home/flasky

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt 

COPY . . 

CMD ["gunicorn", "flasky:app", "--bind", "0.0.0.0:5000"]  


