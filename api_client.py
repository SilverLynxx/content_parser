import asyncio
from aiohttp import ClientSession
import re


class ApiClient:

    def __init__(self):
        # self.CURRENT_SESSION = ''
        self.cookies = {}
        self.root_url = 'http://0.0.0.0:8080'
        self.http_session = ClientSession()

    async def _post(self, url='/', json_data={}):
        async with self.http_session.post(
            f'{self.root_url}{url}', json=json_data, cookies=self.cookies) as resp:
            print(resp.status)
            return await resp.json(), resp.cookies

    async def close(self):
        await self.http_session.close()


    async def login(self, username: str, password: str):

        login_url = '/api/login'
        data = {'username': username, 'password':password}

        resp, cookies = await self._post(url=login_url, json_data=data)
        self.cookies = cookies
        return resp


    async def create_record(self, record_headline: str, record_text: str, tags: list):


        login_url = '/api/create_record'
        data = {'record_headline': record_headline, 'record_text': record_text, 'tags': tags}
        
        resp = await self._post(url=login_url, json_data=data)
        return resp

    async def set_record_media(
        self, recordid: str, media_data: str, media_type: str, media_description: str):

        login_url = '/api/set_record_media'
        data = {
            'recordid': recordid, 
            'media_data': media_data, 
            'media_type': media_type, 
            'media_description': media_description }
        resp = await self._post(url=login_url, json_data=data)
        return resp


async def main():
    username = 'admin'
    password = '123456'
    record_headline = 'TEST'
    record_text = 'PAAAMM!'
    tags = ['test', 'tag']

    apiClient = ApiClient()

    login_resp = await apiClient.login(username, password)
    create_record_resp = await apiClient.create_record(record_headline, record_text, tags)

    media_type = 'embedded_video'
    media_data = {'url': 'https://sovetromantica.com/embed/episode_804_1-subtitles'}
    media_description = 'description'

    print(create_record_resp)
    recordid = create_record_resp[0]['data']['recordid']

    set_record_media_resp = await apiClient.set_record_media(recordid, media_data, media_type, media_description)

    await apiClient.close()
    print(set_record_media_resp)


if __name__ == '__main__':

    asyncio.run(main())