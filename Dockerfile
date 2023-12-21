FROM ubuntu:latest

# Pull official base image
FROM python:3.12-slim-bullseye

RUN apt-get  update && \
    apt-get install -y  curl libpq-dev gcc python3-cffi  && \
    apt-get clean autoclean && \
    apt-get autoremove --purge -y

# set work directory
WORKDIR /usr/app

# Copying src code to Container
COPY . /usr/app
COPY .env /usr/app/.env

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "manage.py", "bot"]