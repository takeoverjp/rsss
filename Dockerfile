FROM python:3.8-slim-buster
COPY requirements.txt requirements.txt
COPY . .
RUN apt-get update
RUN apt-get install -y zip
RUN mkdir package/
RUN cp *.py package/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
