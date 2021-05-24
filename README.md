# CulpInt
Python-based web interface for Recon-ng.
## Installation
Culpint requires at least Python 3.7 (others are untested). It also requires a decent
version of MariaDB (other SQL db type can be adjusted in the config file).
... Updated later
## Running
### For production
```
gunicorn --bind 0.0.0.0:9012 app:app # updated later
```
### For development
```
python app.py
```

## License
This project is licensed using MIT license.
