import os
import queue
import subprocess
import threading

from flask import current_app, request
from flask_socketio import emit

from . import socketio
from .utils import escape_ansi
from .views import requires_auth

clients = {}


@socketio.on('connect')
@requires_auth
def connect():
    print('connected with client:', request.sid)
    clients[request.sid] = {'rng_proc': None}
    print('clients:', clients)


@socketio.on('disconnect')
@requires_auth
def disconnect():
    print('client disconnected:', request.sid)
    proc = clients[request.sid]['rng_proc']
    if proc is not None and proc.poll() is not None:
        proc.kill()
    clients.pop(request.sid)


@socketio.on('init rng')
@requires_auth
def rng_streamer():
    emit('stdout', 'Socket ID: %s\n' % request.sid, room=request.sid)
    emit('stdout', 'Initializing Recon-ng, please wait...\n', room=request.sid)
    rng_exec = os.path.join(current_app.root_path, 'recon-ng', 'recon-ng')
    proc = subprocess.Popen([rng_exec],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    sid = request.sid
    clients[sid]['rng_proc'] = proc

    q = queue.Queue()
    reader_lock = threading.Lock()

    def reader():
        while sid in clients and proc.poll() is None:
            out = proc.stdout.read(1024)
            with reader_lock:
                if len(out):
                    q.put(out)
            proc.stdout.flush()

    reader_thread = threading.Thread(target=reader, daemon=True)
    reader_thread.start()

    while request.sid in clients and proc.poll() is None:
        try:
            with reader_lock:
                out = q.get(timeout=.1)
        except queue.Empty:
            continue
        socketio.emit('stdout', escape_ansi(out.decode()), room=request.sid)

    if proc.poll() is not None:
        proc.kill()


@socketio.on('run rng module')
@requires_auth
def run_rng_module(data):
    rng_proc = clients[request.sid]['rng_proc']
    if rng_proc is not None and rng_proc.poll() is not None:
        rng_proc.kill()
    emit('stdout',
         'Initializing... (Socket ID: %s)\n' % request.sid,
         room=request.sid)

    module_name, module_options = data

    rng_exec_args = ['-m', module_name]
    for option, value in module_options.items():
        if not value:
            continue
        rng_exec_args += ['-o', '='.join((option, str(value)))]

    rng_exec = os.path.join(current_app.root_path, 'recon-ng', 'recon-cli')

    proc = subprocess.Popen([rng_exec, *rng_exec_args, '-x', '--stealth'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    sid = request.sid
    clients[sid]['rng_proc'] = proc

    q = queue.Queue()
    reader_lock = threading.Lock()

    def reader():
        while sid in clients and proc.poll() is None:
            out = proc.stdout.read(1024)
            with reader_lock:
                if len(out):
                    q.put(out)
            proc.stdout.flush()

    reader_thread = threading.Thread(target=reader, daemon=True)
    reader_thread.start()

    while request.sid in clients and proc.poll() is None:
        try:
            with reader_lock:
                out = q.get(timeout=.1)
        except queue.Empty:
            continue
        socketio.emit('stdout', escape_ansi(out.decode()), room=request.sid)

    if proc.poll() is not None:
        proc.kill()


@socketio.on('run rng command')
@requires_auth
def run_rng_command(command):
    rng_proc = clients[request.sid]['rng_proc']
    if rng_proc is not None and rng_proc.poll() is not None:
        rng_proc.kill()
    emit('stdout',
         'Initializing... (Socket ID: %s)\n' % request.sid,
         room=request.sid)

    rng_exec = os.path.join(current_app.root_path, 'recon-ng', 'recon-cli')

    proc = subprocess.Popen([rng_exec, '-C', command],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    sid = request.sid
    clients[sid]['rng_proc'] = proc

    q = queue.Queue()
    reader_lock = threading.Lock()

    def reader():
        while sid in clients and proc.poll() is None:
            out = proc.stdout.read(1024)
            with reader_lock:
                if len(out):
                    q.put(out)
            proc.stdout.flush()

    reader_thread = threading.Thread(target=reader, daemon=True)
    reader_thread.start()

    while request.sid in clients and proc.poll() is None:
        try:
            with reader_lock:
                out = q.get(timeout=.1)
        except queue.Empty:
            continue
        socketio.emit('stdout', escape_ansi(out.decode()), room=request.sid)

    if proc.poll() is not None:
        proc.kill()

    socketio.emit('proc exited', room=request.sid)


@socketio.on('stdin')
@requires_auth
def send_rng_input(input):
    rng_proc = clients[request.sid]['rng_proc']
    if not rng_proc:
        return
    emit('stdout', input, room=request.sid)
    rng_proc.stdin.write(input.encode())
    rng_proc.stdin.flush()
