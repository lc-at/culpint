# CulpInt
Python-based web interface for Recon-ng.
## Installation
CulpInt requires at least Python 3.7 (others are untested). It also requires a decent
version of MariaDB (other SQL db type can be adjusted in the config file).
1. If you are using MySQL: `sudo apt install default-libmysqlclient-dev`.
2. `pip install flask flask_sqlalchemy flask_socketio mysqlclient gunicorn eventlet==0.30`.
3. Install recon-ng requirements: `pip install -r app/recon-ng/REQUIREMENTS`.
4. Copy `app/config.py.default` file to `app/config.py` and adjust values inside it.
## Running
### For production
```
gunicorn --worker-class eventlet -w 1 app:app -b 0.0.0.0:7878
```
### For development
```
python app.py
```

## License
This project is licensed using MIT license.
