FROM python:3.9
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1


WORKDIR /pythonNikitka

ADD . /pythonNikitka

COPY ./requirements.txt /pythonNikitka/requirements.txt
COPY . /usr/app
COPY .env /usr/app/.env
RUN pip install -r requirements.txt

COPY . /pythonNikitka
CMD ["python","manage.py","bot"]