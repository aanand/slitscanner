FROM ubuntu:15.04

RUN set -ex; \
    apt-get update -qq; \
    apt-get -y install \
      ffmpeg \
      git \
      imagemagick \
      libopencv-dev \
      libpq-dev \
      ocl-icd-opencl-dev \
      python-dev \
      python-opencv \
      python-pip \
      python-psycopg2 \
      virtualenv \
    ; \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/dthpham/butterflow.git /butterflow
RUN pip install /butterflow

RUN mkdir /code
WORKDIR /code

ADD requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

ADD . /code

ENV PYTHONUNBUFFERED 1
CMD python bot.py
