FROM heroku/heroku:20
LABEL maintainer="Ghost Proxy"
ENV PY_VER_MAJOR "3.8"
ENV UBUNTU_RELEASE_NAME focal
ENV DEBIAN_FRONTEND noninteractive

RUN sed -i "s=http://archive.ubuntu.com/ubuntu/=$(wget -qO- http://mirrors.ubuntu.com/mirrors.txt | head -n 1)=" /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -qq --no-install-recommends \
        python${PY_VER_MAJOR}-dev \
        python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US.UTF-8

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN python${PY_VER_MAJOR} -m pip install -U pip

RUN mkdir -p /app/voluspa
COPY . /app/voluspa/
WORKDIR /app/voluspa

RUN pip3 install -r requirements.txt

# Dockerfile Build

    # docker build . -t voluspa

# Running the container

    # Mac/Nix
    # docker run -it voluspa:latest python3.8 ./voluspa.py

    # Powershell (at this stage, mounting works in rw mode with WSL2+ backend)
    # docker run -it -v ${pwd}:/app/voluspa voluspa:latest python3.8 ./voluspa.py
