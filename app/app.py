import logging

from aiohttp import web

from app import db
from app import middleware
from app.api import root as root_api
from app.api import samples as samples_api
from app.api import users as users_api

LOG = logging.getLogger(__name__)


async def init_app() -> web.Application:

    LOG.info('Initializing Python AioHTTP birds API')

    app = web.Application(middlewares=[
        middleware.shield_mutating_request, middleware.sign_off,
        middleware.authorize
    ])
    app.router.add_get('/', root_api.index_handler)

    bird_samples_app = web.Application()
    bird_samples_app.router.add_view('/{sample_name}', samples_api.BirdSamples)
    bird_samples_app.add_routes([
        web.get('', samples_api.list_all),
        web.post('', samples_api.upload_many)
    ])

    admin_app = web.Application(middlewares=[middleware.requires_admin_access])
    admin_app.router.add_view('', users_api.Users)
    admin_app.router.add_view('/{username:[a-z]+}', users_api.User)

    app.add_subapp('/api/samples', bird_samples_app)
    app.add_subapp('/admin/users', admin_app)

    db.setup(app)

    return app