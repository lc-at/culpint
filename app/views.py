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
        return f(*args, **kwargs)

    return decorated


@app.route('/')
@requires_auth
def root():
    return render_template('recon-ng.html')


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
            flash('Pengguna dengan nama tersebut sudah ada.', 'danger')
        elif not re.match(r'^[a-z]+$', username):
            flash('Nama pengguna harus hanya terdiri dari huruf kecil.',
                  'danger')
        else:
            User.create_user(username, password)
            flash('Pengguna berhasil ditambahkan.', 'success')
            return redirect(url_for('users'))

    return render_template('user/add.html')


@app.route('/switch-user/<int:id>')
@requires_auth
def switch_user(id):
    user = User.query.filter_by(id=id).first()
    if 'su' not in session or not user:
        abort(404)
    session.pop('su')
    session['username'] = user.username
    flash('Berhasil mengganti user.', 'success')
    return redirect(url_for('root'))


@app.route('/delete-user/<int:id>')
@requires_auth
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if 'su' not in session or not user:
        abort(404)
    elif user.username == app.config['SU_USERNAME']:
        flash('Pengguna super tidak diperbolehkan untuk dihapus.', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('Pengguna berhasil dihapus.', 'success')
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
            flash('Selamat datang!', 'success')
            session['authed'] = True
            session['username'] = username
            session['su'] = username == app.config['SU_USERNAME']
            return redirect(url_for('root'))
        else:
            flash('Terjadi kesalahan. Nama pengguna atau kata sandi salah.',
                  'danger')
    return render_template('user/login.html')


@app.route('/change-password', methods=['GET', 'POST'])
@requires_auth
def change_password():

    if request.method == 'POST':
        password = request.form.get('passwd')
        cpassword = request.form.get('cpasswd')
        if not (password and cpassword) or cpassword != password:
            flash('Kata sandi tidak diubah.', 'warning')
        else:
            User.change_password(session['username'], password)
            flash('Kata sandi berhasil diubah.', 'success')
            return logout()
    return render_template('user/change_password.html')


@app.route('/logout')
@requires_auth
def logout():
    session.pop('authed')
    session.pop('username')
    if session.get('su'):
        session.pop('su')
    flash('Anda telah berhasil keluar.', 'info')
    return redirect(url_for('login'))
