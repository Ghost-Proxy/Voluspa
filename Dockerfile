FROM buildpack-deps:20.04-curl
LABEL maintainer="Ghost Proxy"
ENV PY_VER_MAJOR "3.9"
ENV UBUNTU_RELEASE_NAME focal
ENV DEBIAN_FRONTEND noninteractive

RUN sed -i "s=http://archive.ubuntu.com/ubuntu/=$(wget -qO- http://mirrors.ubuntu.com/mirrors.txt | head -n 1)=" /etc/apt/sources.list && \
    echo "deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu ${UBUNTU_RELEASE_NAME} main" >> /etc/apt/sources.list && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F23C5A6CF475977595C89F51BA6932366A755776

RUN apt-get update && \
    apt-get install -qq --no-install-recommends \
        locales \
        build-essential \
        python${PY_VER_MAJOR} \
        python${PY_VER_MAJOR}-dev \
        python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN python${PY_VER_MAJOR} -m pip install -U pip && \
    pip3 install wheel

RUN mkdir -p /app/voluspa
COPY . /app/voluspa/
WORKDIR /app/voluspa

RUN pip3 install -r requirements.txt

# Dockerfile Build

    # docker build . -t voluspa

# Running the container

    # Mac/Nix
    # docker run -it voluspa:latest python3.9 ./voluspa.py

    # Powershell (at this stage, mounting works in rw mode with WSL2+ backend)
    # docker run -it -v ${pwd}:/app/voluspa voluspa:latest python3.9 ./voluspa.py
