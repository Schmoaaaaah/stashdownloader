FROM python:3.10.5-alpine

RUN mkdir -p /app
RUN mkdir -p /temp
RUN mkdir -p /media
RUN apk add ffmpeg aria2 gcc musl-dev
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY ./log.py /app/log.py
COPY ./stash_interface.py /app/stash_interface.py
COPY main.py /app/main.py


CMD ["python", "main.py"]