# voluspa

> **// Ghost Proxy** / Proto-Warmind AI
> _Destiny 2 Discord Bot_

![Voluspa Logo](images/voluspa/Voluspa_icon_100x133_black.png)

---

### Local Docker for development

A **Dockerfile** is provided that will also automagically setup a bot environment for local development, running, and debugging.

#### Dockerfile Build

```
docker build . -t voluspa
```

#### Running the container

```
docker run -it voluspa:latest python3.8 ./voluspa.py
```

---

### Setup

So you like doing things the hard way, that's totally cool also! Here are some instructions to run everything natively, GLHF!

#### Requirements

-   Uses Python 3.11.2
-   Setup assumes Debian based package manager
-   Setup shows how to install Python using the [Deadsnakes PPA](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa)
-   If using Ubuntu 20.04 "Focal Fossa", you won't need to add the Deadsnakes PPA, as Python 3.8 is bundled with the OS

#### Install Steps

1. Install the bare essentials

    `apt update && apt install git software-properties-common`

2. Add the Deadsnakes PPA

    `apt-add-repository ppa:deadsnakes/ppa && apt update`

3. Install Python and related packages

    `apt install python3.11 python3.11-dev python3.11-venv python3-pip`

4. Clone the Voluspa repository

    `git clone https://github.com/Ghost-Proxy/Voluspa.git && cd Voluspa/`

5. These packages may be necessary to build from source if binaries aren't available for Voluspa's dependencies

    `apt install build-essentials libfreetype6-dev`

6. Create and enter a virtual environment

    `python3.11 -m venv ./venv && source venv/bin/activate`

    (_To deactivate a virtual environment, just type_ `deactivate`)

7. Upgrade pip

    `python3.11 -m pip install -U pip`

8. If building dependencies from source, you will need wheel

    `python3.11 -m pip install wheel`

9. Install dependencies

    `pip3 install -r requirements.txt`

10. Create (and populate) a secrets file, or set secrets in your environment

**WARNING:** **DO NOT** share or commit your secrets. Accidental commits should be prevented by the .gitignore

    `cp config/config.yaml config/secrets.yaml`

11. Start Voluspa

    `python3.11 voluspa.py`

12. Happy coding and have fun!

---

💜
