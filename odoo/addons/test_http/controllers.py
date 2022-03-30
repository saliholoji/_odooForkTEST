# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request

from odoo.addons.web.controllers.utils import ensure_db

_logger = logging.getLogger(__name__)


CT_JSON = {'Content-Type': 'application/json; charset=utf-8'}
WSGI_SAFE_KEYS = {'PATH_INFO', 'QUERY_STRING', 'RAW_URI', 'SCRIPT_NAME', 'wsgi.url_scheme'}


class TestHttp(http.Controller):

    # =====================================================
    # Greeting
    # =====================================================
    @http.route(['/test_http/greeting', '/test_http/greeting-none'], type='http', auth='none')
    def greeting_none(self):
        return "Tek'ma'te"

    @http.route('/test_http/greeting-public', type='http', auth='public')
    def greeting_public(self):
        assert request.env.user, "ORM should be initialized"
        return "Tek'ma'te"

    @http.route('/test_http/greeting-user', type='http', auth='user')
    def greeting_user(self):
        assert request.env.user, "ORM should be initialized"
        return "Tek'ma'te"

    @http.route('/test_http/wsgi_environ', type='http', auth='none')
    def wsgi_environ(self):
        environ = {
            key: val for key, val in request.httprequest.environ.items()
            if (key.startswith('HTTP_')  # headers
             or key.startswith('REMOTE_')
             or key.startswith('REQUEST_')
             or key.startswith('SERVER_')
             or key.startswith('werkzeug.proxy_fix.')
             or key in WSGI_SAFE_KEYS)
        }

        return request.make_response(
            json.dumps(environ, indent=4),
            headers=list(CT_JSON.items())
        )

    # =====================================================
    # Echo-Reply
    # =====================================================
    @http.route('/test_http/echo-http-get', type='http', auth='none', methods=['GET'])
    def echo_http_get(self, **kwargs):
        return str(kwargs)

    @http.route('/test_http/echo-http-post', type='http', auth='none', methods=['POST'], csrf=False)
    def echo_http_post(self, **kwargs):
        return str(kwargs)

    @http.route('/test_http/echo-http-csrf', type='http', auth='none', methods=['POST'], csrf=True)
    def echo_http_csrf(self, **kwargs):
        return str(kwargs)

    @http.route('/test_http/echo-json', type='json', auth='none', methods=['POST'], csrf=False)
    def echo_json(self, **kwargs):
        return kwargs

    @http.route('/test_http/echo-json-context', type='json', auth='user', methods=['POST'], csrf=False)
    def echo_json_context(self, **kwargs):
        return request.env.context

    # =====================================================
    # Models
    # =====================================================
    @http.route('/test_http/<model("test_http.galaxy"):galaxy>', auth='public')
    def galaxy(self, galaxy):
        if not galaxy.exists():
            raise UserError('The Ancients did not settle there.')

        return http.request.render('test_http.tmpl_galaxy', {
            'galaxy': galaxy,
            'stargates': http.request.env['test_http.stargate'].search([
                ('galaxy_id', '=', galaxy.id)
            ]),
        })

    @http.route('/test_http/<model("test_http.galaxy"):galaxy>/<model("test_http.stargate"):gate>', auth='user')
    def stargate(self, galaxy, gate):
        if not gate.exists():
            raise UserError("The goa'uld destroyed the gate")

        return http.request.render('test_http.tmpl_stargate', {
            'gate': gate
        })

    # =====================================================
    # Cors
    # =====================================================
    @http.route('/test_http/cors_http_default', type='http', auth='none', cors='*')
    def cors_http(self):
        return "Hello"

    @http.route('/test_http/cors_http_methods', type='http', auth='none', methods=['GET', 'PUT'], cors='*')
    def cors_http_verbs(self, **kwargs):
        return "Hello"

    @http.route('/test_http/cors_json', type='json', auth='none', cors='*')
    def cors_json(self, **kwargs):
        return {}

    # =====================================================
    # Dual nodb/db
    # =====================================================
    @http.route('/test_http/ensure_db', type='http', auth='none')
    def ensure_db_endpoint(self, db=None):
        ensure_db()
        assert request.db, "There should be a database"
        return request.db
