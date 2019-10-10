import logging

from aiohttp import web

from app.api import root as root_api
from app.api import samples as samples_api

LOG = logging.getLogger(__name__)

LOG.info('Initializing Python AioHTTP birds API')

app = web.Application()
app.router.add_get('/', root_api.index_handler)

# bird samples api
app.router.add_view('/api/samples/{sample_name}', samples_api.BirdSamples)
app.add_routes([web.get('/api/samples',
                        samples_api.list_all)])  # aiohttp.web.AbstractRouteDef
