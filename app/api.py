from flask import Blueprint, abort, jsonify, current_app

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/recon-ng/list_modules')
def rng_list_modules():
    return jsonify(current_app.rng_api.get_module_names())


@bp.route('/recon-ng/module/<path:m_name>')
def rng_module_details(m_name):
    module = current_app.rng_api.get_module_details(m_name)
    if not module:
        abort(404)
    return jsonify(module.meta)
