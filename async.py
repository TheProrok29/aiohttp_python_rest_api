import asyncio
import aiohttp
from pathlib import Path
import yarl

CHUNK_SIZE = 4096

MP3_BASE = 'http://www.birdsinbackyards.net/sites/www.birdsinbackyards.net/files/factsheets/audio'
MP3 = (
    yarl.URL(f'{MP3_BASE}/eudynamys-scolopacea.mp3'),
    yarl.URL(f'{MP3_BASE}/cythrops-novaehollandiae.mp3'),
    yarl.URL(f'{MP3_BASE}/ninox-novaeseelandiae.mp3'),
    yarl.URL(f'{MP3_BASE}/podargus-strigoides.mp3'),
    yarl.URL(f'{MP3_BASE}/cracticus-torquatus.mp3'),
    yarl.URL(f'{MP3_BASE}/rhipidura-leucophrys.mp3'),
    yarl.URL(f'{MP3_BASE}/vanellus-miles.mp3'),
    yarl.URL(f'{MP3_BASE}/anthochaera-chrysoptera.mp3'),
    yarl.URL(f'{MP3_BASE}/corvus-coronoides_0.mp3'),
    yarl.URL(f'{MP3_BASE}/calyptorhynchus-funereus.mp3'),
    yarl.URL(f'{MP3_BASE}/gymnorhina-tibicen.mp3'),
    yarl.URL(f'{MP3_BASE}/strepera-graculina.mp3'),
    yarl.URL(f'{MP3_BASE}/dacelo-novaeguineae.mp3'),
    yarl.URL(f'{MP3_BASE}/anthochaera-carnunculata.mp3'),
    yarl.URL(f'{MP3_BASE}/streptopelia-chinensis.mp3'),
    yarl.URL(f'{MP3_BASE}/cacatua-galerita.mp3'),
    yarl.URL(f'{MP3_BASE}/grallina-cyanoleuca.mp3'),
    yarl.URL(f'{MP3_BASE}/cacatua-roseicapilla.mp3'),
    yarl.URL(f'{MP3_BASE}/manorina-melanocephala.mp3'),
    yarl.URL(f'{MP3_BASE}/pycnonotus-jocosus.mp3'),
    yarl.URL(f'{MP3_BASE}/coracina-novaehollandiae.mp3'),
    yarl.URL(f'{MP3_BASE}/aegotheles-cristatus.mp3'),
    yarl.URL(f'{MP3_BASE}/ninox-strenua.mp3'),
    yarl.URL(f'{MP3_BASE}/cacomantis-flabelliformis.mp3'),
    yarl.URL(f'{MP3_BASE}/cuculus-pallidus.mp3'),
    yarl.URL(f'{MP3_BASE}/cacomantis-variolosus.mp3'),
    yarl.URL(f'{MP3_BASE}/turdus-merula.mp3'),
    yarl.URL(f'{MP3_BASE}/acridotheres-tristis.mp3'),
    yarl.URL(f'{MP3_BASE}/sturnus-vulgaris.mp3'),
    yarl.URL(f'{MP3_BASE}/oriolus-sagittatus.mp3'),
    yarl.URL(f'{MP3_BASE}/alisterus-scapularis.mp3'),
    yarl.URL(f'{MP3_BASE}/trichoglossus-haematodus.mp3'),
    yarl.URL(f'{MP3_BASE}/platycercus-elegans.mp3'),
    yarl.URL(f'{MP3_BASE}/pardalotus-punctatus.mp3'),
    yarl.URL(f'{MP3_BASE}/malurus-cyaneus.mp3'),
    yarl.URL(f'{MP3_BASE}/zosterops-lateralis.mp3'),
    yarl.URL(f'{MP3_BASE}/cacatua-tenuirostris.mp3'),
    yarl.URL(f'{MP3_BASE}/phylidonyris-novaehollandiae.mp3'),
    yarl.URL(f'{MP3_BASE}/sphecotheres-viridis.mp3'),
)


async def main(download_dir: Path) -> None:
    async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
        await asyncio.gather(*[download(mp3_url, download_dir, session) for mp3_url in MP3])


async def download(mp3_url: yarl.URL, download_dir: Path, session: aiohttp.ClientSession) -> None:
    async with session.get(mp3_url) as resp:
        if resp.headers['Content-Type'] == 'audio/mpeg':
            mp3_file = download_dir / mp3_url.parts[-1]
            mp3_file.touch()
            with mp3_file.open('wb') as mp3_handle:
                async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                    mp3_handle.write(chunk)


if __name__ == '__main__':
    download_dir = Path.home() / 'Pobrane' / 'birds_sample2'
    download_dir.mkdir(exist_ok=True)

    asyncio.run(main(download_dir))
