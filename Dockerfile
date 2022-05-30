FROM python:3.9-slim

LABEL author='Edward' version=1.0 description="taxBot for telegram"

RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

RUN apt-get upgrade -y

ENV LANG ru_RU.UTF-8

ENV LANGUAGE ru_RU:ru

ENV LC_ALL ru_RU.UTF-8

RUN mkdir /app

COPY src /app

COPY requirements.txt /app

WORKDIR /app

RUN python -m pip install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["python", "app.py"]