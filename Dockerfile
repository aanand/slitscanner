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
      virtualenv \
    ; \
    rm -rf /var/lib/apt/lists/*

RUN pip install git+git://github.com/dthpham/butterflow.git@48d3fca11c21f6680839ea9789eb928791a22b3e

RUN mkdir /code
WORKDIR /code

ADD requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

ADD . /code

ENV PYTHONUNBUFFERED 1
CMD python bot.py
