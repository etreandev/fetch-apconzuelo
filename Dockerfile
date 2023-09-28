FROM python:3.9-slim

COPY . .

RUN pip install -r requirements.txt

WORKDIR /etl_app

CMD ["python", "main.py"]