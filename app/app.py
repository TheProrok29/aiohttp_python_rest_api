import logging

from aiohttp import web

from app import middleware
from app.api import root as root_api
from app.api import samples as samples_api
from app.api import users as users_api

LOG = logging.getLogger(__name__)

LOG.info('Initializing Python AioHTTP birds API')

app = web.Application(middlewares=[middleware.shield_mutating_request, middleware.sign_off, middleware.authorize]) 
app.router.add_get('/', root_api.index_handler)

# bird samples api
app.router.add_view('/api/samples/{sample_name}', samples_api.BirdSamples)
app.add_routes([
    web.get('/api/samples', samples_api.list_all),
    web.post('/api/samples', samples_api.upload_many)
])  # aiohttp.web.AbstractRouteDef

# users api
app.router.add_view('/admin/users', users_api.Users)
app.router.add_view('/admin/users/{username:[a-z]+}', users_api.User)