import asyncio
import asyncpg
import re
from jikanpy import AioJikan
from jikanpy.exceptions import APIException
from aiohttp.client_exceptions import ContentTypeError
from config import Config
from asyncpg.exceptions import UniqueViolationError
from hashlib import md5
import datetime
from random import randint
import re

from db_handler import DbHandler
from api_client import ApiClient

from parse_sovetromantica import parse_sovetromantica


def recid_gen():
    return 'recid_' + md5(
        (
            str(datetime.datetime.now()) + \
            str(randint(1000, 9999))
        ).encode('utf-8')).hexdigest()

async def test_containing_db(loop):


    async def write_data_to_db(record, recid, tags, db=None):

        await db.insert_to_table('records', record)
        for tag in tags:
            try:
                await db.insert_to_table('tags', {'tagname': tag}, ignore_conflict=['tagname',])
            except UniqueViolationError:
                pass
            try:
                await db.insert_to_table('records_tags', {'tagname': tag, 'recordid': recid})
            except UniqueViolationError:
                pass

    aio_jikan = AioJikan(loop=loop)

    cfg = Config()
    pg_pool = await asyncpg.create_pool(cfg.DB_ADDRESS)
    db = DbHandler(pg_pool=pg_pool, cfg=cfg)

    
    year_2000 = 2000
    seasons = ['winter', 'spring', 'summer', 'fall']

    for year in range(2015, 2019):
        for season in seasons:

            print(f'[+] reading {season} in {year}')

            season_year = await aio_jikan.season(year=year, season=season)


            for item in season_year['anime']:
                title = item['title']
                title_tag = ('_'.join(re.findall(r'\W?(\w+)\W?', title))).lower()
                recid = recid_gen()
                record = {
                    'recordid': recid,
                    'username': 'admin',
                    'record_headline': title,
                    'record_text': f'{title} ({season} {year})'
                }
                tags = [title_tag, str(year), season]
                await write_data_to_db(record, recid, tags, db=db)

    await aio_jikan.close()
    await pg_pool.close()

async def main(loop):

    aio_jikan = AioJikan(loop=loop)
    
    year = 2019
    season = 'spring'
    season_year = await aio_jikan.season(year=year, season=season)
    root_url = 'https://sovetromantica.com'
    apiSesson = ApiClient()
    await apiSesson.login('admin', '123456')

    season_anime = season_year['anime']
    for anime in season_anime:
        print('\n',anime['title'])
        embed_links_sub, embed_links_dub = await parse_sovetromantica(anime['title'], 'anime')
        for link in embed_links_sub:
            num = int(re.findall(r'_(\d*?)-subtitles', link)[-1])
            num_len = len(str(num))
            ep_num = ''
            if num_len == 1:
                ep_num = f'e00{num}'
            if num_len == 2:
                ep_num = f'e0{num}'
            if num_len == 3:
                ep_num = f'e{num}'
            record_headline = f'{anime["title"]} ({ep_num}) (sub) [sovetromantica]'
            record_text = f'{anime["title"]} ({ep_num}) [{season} {year}]'
            tags = []
            tags.append(('_'.join(re.findall(r'\W?(\w+)\W?', anime['title']))).lower())
            tags.append(str(year))
            tags.append(f'{season}_{year}')
            tags.append('sub')
            tags.append(ep_num)
            record_resp = await apiSesson.create_record(record_headline, record_text, tags)
            recordid = record_resp[0]['data']['recordid']
            media_data = {'url': f'{root_url}{link}'}
            media_type = 'embedded_video'
            media_description = f'{anime["title"]} ({ep_num}) (sub) [sovetromantica]'
            media_resp = await apiSesson.set_record_media(recordid, media_data, media_type, media_description)
        for link in embed_links_dub:
            num = int(re.findall(r'_(\d*?)-dubbed', link)[-1])
            num_len = len(str(num))
            ep_num = ''
            if num_len == 1:
                ep_num = f'e00{num}'
            if num_len == 2:
                ep_num = f'e0{num}'
            if num_len == 3:
                ep_num = f'e{num}'
            record_headline = f'{anime["title"]} ({ep_num}) (dub) [sovetromantica]'
            record_text = f'{anime["title"]} ({ep_num}) [{season} {year}]'
            tags = []
            tags.append(('_'.join(re.findall(r'\W?(\w+)\W?', anime['title']))).lower())
            tags.append(str(year))
            tags.append(f'{season}_{year}')
            tags.append('dub')
            tags.append(ep_num)
            record_resp = await apiSesson.create_record(record_headline, record_text, tags)
            recordid = record_resp[0]['data']['recordid']
            media_data = {'url': f'{root_url}{link}'}
            media_type = 'embedded_video'
            media_description = f'{anime["title"]} ({ep_num}) (dub) [sovetromantica]'
            media_resp = await apiSesson.set_record_media(recordid, media_data, media_type, media_description)

    await aio_jikan.close()


if __name__ == '__main__':
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))