# voluspa
> **// Ghost Proxy** / Proto-Warmind AI  
> _Destiny 2 Discord Bot_

![Voluspa Logo](images/voluspa/Voluspa_icon_100x133_black.png)

---

### Setup
- Uses Python 3.8.6

1. Install Python 3.8.6
2. Grab [virtualenv](https://virtualenv.pypa.io/en/latest/installation/): `pip install --user virtualenv`
3. Clone _Voluspa_ source `git clone https://github.com/Ghost-Proxy/Voluspa.git`
4. Create a virtualenv: `virtualenv venv`
5. Activate the virtual env (depends on OS): 
  - linux (sh): `source ./venv/bin/activate` 
  - windows (ps): `./venv/Scripts/activate.ps1`
6. Install pip requirements: `pip install -r requirements.txt`
7. Happy coding and have fun!

(_To deactivate a virtualenv, just type_ `deactivate`)


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
