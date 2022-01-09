# CulpInt
CulpInt is a multi-user Python-based web interface for Recon-ng. Simply put, it is mainly just a web terminal connected to a Recon-ng process. Aside from the web terminal, it also have a few dedicated web interface for some handy features below:
- Run a module
- Marketplace
- Manage API Keys

![image](https://user-images.githubusercontent.com/30001379/148701387-275b3437-5d99-4fa9-bfb5-b35a991ebfde.png)

CulpInt is meant to be used as a quick way to access a Recon-ng. It may also be useful when working in a team or when you just want to teach some people on how to use Recon-ng.

Thanks to [kalpinus](https://github.com/kalpinus) for making this project happen.

## Installation and Deployment
CulpInt requires at least Python 3.7 (others are untested). Use of virtual environment like `venv` is strongly encouraged. It also requires a decent
version of MariaDB (other SQL database type can be adjusted in the config file).
1. If you are using MySQL and on a Debian-based system: `sudo apt install default-libmysqlclient-dev`. If not, then do something similar that works ;).
2. `pip install flask flask_sqlalchemy flask_socketio mysqlclient gunicorn eventlet==0.30`.
3. Initialize the git submodule: `git submodule --init --recursive`
4. Install Recon-ng requirements: `pip install -r app/recon-ng/REQUIREMENTS`.
5. Copy `app/config.py.default` file to `app/config.py` and adjust values inside it accordingly.

### Deployment
Default credential:
- Username: `superuser`
- Password: `password`
#### For production
Using gunicorn
```
gunicorn --worker-class eventlet -w 1 app:app -b 0.0.0.0:7878
```
#### For development
Using the default development server:
```
python app.py
```

### Your first-run
When you open the marketplace page and saw that there is no modules listed: try refreshing the Recon-ng marketplace index by running this command in the Recon-ng web interface
```
marketplace refresh
```

## Contribution
Any form of contribution will be highly appreciated.

## License
This project is licensed using MIT license.
