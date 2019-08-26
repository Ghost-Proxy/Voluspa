FROM ubuntu:16.04
LABEL maintainer="Mirage"
ENV PY_VER="3.7.2"
ENV PY_VER_MAJOR="3.7"
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -qq \
        locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN apt-get update && \
    apt-get install -qq \
        apt-utils \
        build-essential \
        curl \
        libffi-dev \
        libgdbm-dev \
        libncurses5-dev \
        libnss3-dev \
        libreadline-dev \
        libssl-dev \
        libsqlite3-dev \
        software-properties-common \
        wget \
        zlib1g-dev

RUN cd /opt && \
    curl https://www.python.org/ftp/python/${PY_VER}/Python-${PY_VER}.tar.xz -o Python-${PY_VER}.tar.xz && \
    tar -xf Python-${PY_VER}.tar.xz && \
    cd Python-${PY_VER} && \
    ./configure --enable-optimizations && \
    make -j $(getconf _NPROCESSORS_ONLN) install

RUN python${PY_VER_MAJOR} --version && \
    python${PY_VER_MAJOR} -m pip install -U pip

RUN mkdir -p /app/voluspa
ADD . /app/voluspa/
COPY . /app/voluspa/
WORKDIR /app/voluspa

RUN pip3 install -r requirements.txt

# Dockerfile Build

    # docker build . -t voluspa:local

# Running the container

    # Mac/Nix
    # docker run -it -v $(pwd):/app/voluspa voluspa:local python3 ./voluspa.py

    # Powershell
    # docker run -it -v ${$pwd.Path}:/app/voluspa voluspa:local python3 ./voluspa.py
