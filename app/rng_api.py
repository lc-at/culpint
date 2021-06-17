import contextlib
import os
import sys

from . import app

sys.path.insert(1, os.path.join(app.root_path, 'recon-ng'))  # noqa

from recon.core import base  # type: ignore # noqa


class CulpintReconNgAPI:
    _base = None

    def __init__(self):
        self.reload()

    def _spawn_base(self):
        rng_base = base.Recon()
        with contextlib.redirect_stdout(open(os.devnull, 'w')):
            rng_base.start(base.Mode.CLI)
        return rng_base

    def reload(self):
        self._base = self._spawn_base()

    def get_module_names(self):
        return list(self._base._loaded_modules.keys())

    def get_module_details(self, module_name):
        return self._base._loaded_modules.get(module_name)

    def get_api_keys(self):
        return self._base._query_keys('select * from keys')

    def add_api_key(self, name, value):
        result = self._base._query_keys('UPDATE keys SET value=? WHERE name=?',
                                        (value, name))
        if not result:
            return self._base._query_keys('INSERT INTO keys VALUES (?, ?)',
                                          (name, value))
        return result

    def remove_api_key(self, name):
        return self._base._query_keys('DELETE FROM keys WHERE name=?',
                                      (name, ))
