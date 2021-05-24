import re
from functools import wraps

from flask import (abort, flash, redirect, render_template, request, session,
                   url_for)

from . import app
from .models import User, db


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'authed' not in session:
            return redirect(url_for('login'))
        elif request.endpoint != 'logout' and \
                not User.validate_token(session['username'], session['token']):
            flash('Token expired. Please log in again.', 'info')
            return logout()
        session['token'] = User.generate_token(session['username'])
        return f(*args, **kwargs)

    return decorated


@app.route('/')
@requires_auth
def root():
    return redirect(url_for('rng_web'))


@app.route('/rng_interactive')
@requires_auth
def rng_interactive():
    return render_template('rng_interactive.html')


@app.route('/rng_web')
@requires_auth
def rng_web():
    return render_template('rng_web.html')


@app.route('/users')
@requires_auth
def users():
    if 'su' not in session:
        abort(404)
    users = User.query.all()
    return render_template('user/manage.html', rows=users)


@app.route('/add-user', methods=['GET', 'POST'])
@requires_auth
def add_user():
    if 'su' not in session:
        abort(404)
    username = request.form.get('username')
    password = request.form.get('password')
    if request.method == 'POST' and (username and password):
        if User.query.filter_by(username=username).first():
            flash('Username already exist.', 'danger')
        elif not re.match(r'^[a-z]+$', username):
            flash('Username can only contain lowercase letters.', 'danger')
        else:
            User.create_user(username, password)
            flash('User successfully added.', 'success')
            return redirect(url_for('users'))

    return render_template('user/add.html')


@app.route('/switch-user/<int:id>')
@requires_auth
def switch_user(id):
    user = User.query.filter_by(id=id).first()
    if 'su' not in session or not user:
        abort(404)
    elif user.username == session['username']:
        flash('Unable to switch to the same user.', 'danger')
    else:
        session.pop('su')
        session['username'] = user.username
        flash('User successfully switched.', 'success')
    return redirect(url_for('root'))


@app.route('/delete-user/<int:id>')
@requires_auth
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if 'su' not in session or not user:
        abort(404)
    elif user.username == app.config['SU_USERNAME']:
        flash('Unable to delete a superuser.', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User successfully deleted.', 'success')
    return redirect(url_for('users'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'authed' in session:
        return redirect(url_for('root'))
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not (username and password):
            abort(403)
        elif User.authenticate(username, password):
            session['authed'] = True
            session['username'] = username
            session['su'] = username == app.config['SU_USERNAME']
            session['token'] = User.generate_token(username)
            return redirect(url_for('root'))
        else:
            flash('Error. Invalid username or password.', 'danger')
    return render_template('user/login.html')


@app.route('/change-password', methods=['GET', 'POST'])
@requires_auth
def change_password():

    if request.method == 'POST':
        password = request.form.get('passwd')
        cpassword = request.form.get('cpasswd')
        if not (password and cpassword) or cpassword != password:
            flash('Password unchanged.', 'warning')
        else:
            User.change_password(session['username'], password)
            flash('Password changed successfully.', 'success')
            return logout()
    return render_template('user/change_password.html')


@app.route('/logout')
def logout():
    if not session.get('authed'):
        return abort(403)
    session.pop('authed')
    session.pop('username')
    session.pop('token')
    if session.get('su'):
        session.pop('su')
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))
