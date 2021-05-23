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


@socketio.on('disconnect')
@requires_auth
def disconnect():
    print('client disconnected:', request.sid)
    clients.pop(request.sid)


@socketio.on('init rng')
@requires_auth
def rng_streamer():
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
        while sid in clients:
            out = proc.stdout.read(1024)
            with reader_lock:
                q.put(out)
            proc.stdout.flush()

    reader_thread = threading.Thread(target=reader, daemon=True)
    reader_thread.start()

    while request.sid in clients:
        try:
            with reader_lock:
                out = q.get(timeout=.1)
        except queue.Empty:
            continue
        socketio.emit('stdout', escape_ansi(out.decode()), room=request.sid)

    proc.kill()


@socketio.on('stdin')
@requires_auth
def send_rng_input(input):
    rng_proc = clients[request.sid]['rng_proc']
    if not rng_proc:
        return
    emit('stdout', input, room=request.sid)
    rng_proc.stdin.write(input.encode())
    rng_proc.stdin.flush()
