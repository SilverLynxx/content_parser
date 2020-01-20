import asyncio
from aiohttp import ClientSession
import re


async def parse_page(page, http_session):

    target_urls_sub = []
    target_urls_dub = []
    episodes_item_sub = []
    episodes_item_dub = []

    sub_link = re.findall(r'class="view_place">.*?href="(.*?subtitles).*?<\/nav>', page)
    dub_link = re.findall(r'class="view_place">.*?</a><a href="(.*?dubbed)".*?<\/nav>', page)

    if sub_link:
        async with http_session.get(f'https://sovetromantica.com{sub_link[0]}') as resp:
            page_sub = await resp.text()

            episodes_item_sub = [_[-1] for _ in re.findall(
                r'<div class="episodes-slick_item(.*?href="(.*?)".*?)</div>', page_sub)]



    if dub_link:
        async with http_session.get(f'https://sovetromantica.com{dub_link[0]}') as resp:
            page_dub = await resp.text()

            episodes_item_dub = [_[-1] for _ in re.findall(
                r'<div class="episodes-slick_item(.*?href="(.*?)".*?)</div>', page_dub)]

    for ep in episodes_item_sub:
        async with http_session.get(f'https://sovetromantica.com{ep}') as resp_ep:
            page_ep = await resp_ep.text()
            embed_url = re.findall(r'"(\/embed\/.*?)"', page_ep)
            target_urls_sub.append(embed_url[-1])


    for ep in episodes_item_dub:
        async with http_session.get(f'https://sovetromantica.com{ep}') as resp_ep:
            page_ep = await resp_ep.text()
            embed_url = re.findall(r'"(\/embed\/.*?)"', page_ep)
            target_urls_dub.append(embed_url[-1])

    return target_urls_sub, target_urls_dub


async def parse_sovetromantica(title, section):
    
    http_session = ClientSession()

    # title = 'Mugen no Juunin: Immortal'
    # section = 'anime'
    query = ('+'.join(re.findall(r'\W?(\w+)\W?', title))).lower()
    print(query)

    target_urls_sub = []
    target_urls_dub = []
    query_url = f'https://sovetromantica.com/{section}?query={query}'
    async with http_session.get(query_url) as resp:
        page = await resp.text()

        if str(resp.url) == str(query_url):
            print('multiply results')
            url_part = ('-'.join(re.findall(r'\W?(\w+)\W?', title))).lower()
            expr = fr'class="block--full block--shadow".*?href="(\/anime\/\d\d\d-{url_part})".*?class="anime--block__name"'
            res = re.findall(expr, page)
            if len(res) == 1:
                async with http_session.get(f'https://sovetromantica.com{res[0]}') as resp_2:
                    page_2 = await resp_2.text()
                    target_urls_sub, target_urls_dub = await parse_page(page_2, http_session)

        else:
            target_urls_sub, target_urls_dub = await parse_page(page, http_session)

    await http_session.close()

    return target_urls_sub, target_urls_dub


async def main():

    target_urls_sub, target_urls_dub = await parse_sovetromantica('One Punch Man 2nd Season', 'anime')

    # print(result)
    print(target_urls_sub, target_urls_dub)


if __name__ == '__main__':
    asyncio.run(main())