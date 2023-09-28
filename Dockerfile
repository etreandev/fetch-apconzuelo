FROM python:3.9-slim

COPY . .

RUN pip install -r requirements.txt

WORKDIR /etl_app

Run apt update && apt upgrade
run apt install iputils-ping -y
RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "vim"]
CMD ["python", "main.py"]