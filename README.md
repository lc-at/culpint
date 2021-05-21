# culpstocks
Python-based web project for checking stock price signals. Currently available only for checking short-stroke patterns.
## Installation
Culpstocks requires at least Python 3.7 (others are untested). It also requires a decent
version of MariaDB (other SQL db type can be adjusted in the config file).
1. If you are using MySQL: `sudo apt install default-libmysqlclient-dev`.
2. `pip install flask flask_sqlalchemy flask_caching mysqlclient requests gunicorn`.
3. Copy `app/config.py.default` file to `app/config.py` and adjust values inside it.
## Running
### For production
```
gunicorn --bind 0.0.0.0:9012 app:app
```
### For development
```
python app.py
```

## License
This project is licensed using MIT license.
