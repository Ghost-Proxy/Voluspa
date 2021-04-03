# voluspa
> **// Ghost Proxy** / Proto-Warmind AI  
> _Destiny 2 Discord Bot_

![Voluspa Logo](images/voluspa/Voluspa_icon_100x133_black.png)

---

### Setup
- Uses Python 3.9.x
- Setup assumes Debian based package manager
- Setup shows how to install Python using the [Deadsnakes PPA](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa)

1. Install the bare essentials

`apt update && apt install git software-properties-common`
2. Add the Deadsnakes PPA

`apt-add-repository ppa:deadsnakes/ppa && apt update`
3. Install Python and related packages

`apt install python3.9 python3.9-dev python3.9-venv python3-pip`
4. Clone the Voluspa repository

`git clone https://github.com/Ghost-Proxy/Voluspa.git && cd Voluspa/`
5. These packages may be necessary to build from source if binaries aren't available for Voluspa's dependencies

`apt install build-essentials libfreetype6-dev`
6. Create and enter a virtual environment

`python3.9 -m venv ./venv && source venv/bin/activate`
7. Upgrade pip

`python3.9 -m pip install -U pip`
8. If building dependencies from source, you will need wheel

`python3.9 -m pip install wheel`
9. Install dependencies

`pip3 install -r requirements.txt`
10. Create (and populate) a secrets file, or set secrets in your environment

**WARNING:** __DO NOT__ share or commit your secrets. Accidental commits should be prevented by the .gitignore

`cp config/config.yaml config/secrets.yaml`
11. Start Voluspa

`python3.9 voluspa.py`
12. Happy coding and have fun!

(_To deactivate a virtual environment, just type_ `deactivate`)


### Local Docker for development
Additionally, a **Dockerfile** is provided that will also automagically setup a bot environment for local running and debug.

#### Dockerfile Build
```
docker build . -t voluspa
```

#### Running the container
```
docker run -it voluspa:latest python3 ./voluspa.py
```
