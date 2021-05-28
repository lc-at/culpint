import contextlib
import os
import sys

from flask import Blueprint, abort, jsonify

bp = Blueprint('api', __name__, url_prefix='/api')

from . import app  # noqa

sys.path.insert(1, os.path.join(app.root_path, 'recon-ng'))  # noqa

from recon.core import base  # noqa

rng_base = base.Recon()
with contextlib.redirect_stdout(open(os.devnull, 'w')):
    rng_base.start(base.Mode.CLI)


@bp.route('/recon-ng/list_modules')
def rng_list_modules():
    return jsonify(list(rng_base._loaded_modules.keys()))


@bp.route('/recon-ng/module/<path:m_name>')
def rng_module_details(m_name):
    module = rng_base._loaded_modules.get(m_name)
    if not module:
        abort(404)
    return jsonify(module.meta)
