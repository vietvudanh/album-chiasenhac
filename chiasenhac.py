#!/usr/bin/env python3
"""script for downloading album from chiasenhac
usage: chiasenhac.py [-h] --url URL --username USERNAME --password PASSWORD [--quality QUALITY] [--threads NUM_THREADS] [--output OUTPUT_DIR]

download album from chiasenhac.vn

optional arguments:
  -h, --help            show this help message and exit
  --url URL, -u URL     url of the album
  --username USERNAME, -U USERNAME
                        username to login
  --password PASSWORD, -p PASSWORD
                        password to login
  --quality QUALITY, -q QUALITY
                        music quality, 128/320/m4a/flac
  --threads NUM_THREADS, -t NUM_THREADS
                        number of threads
  --output OUTPUT_DIR, -o OUTPUT_DIR
                        output folder
"""
import os
import argparse
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def download_file(params: tuple):
    """download single file"""
    ss, url, album_path, quality = params
    if ss is None:
        ss = requests

    down_page = ss.get(url).text
    down_soup = BeautifulSoup(down_page, 'html.parser')
    filename = down_soup.title.text.split('Download: ')[-1].split(" - ")[0] + "." + quality
    filename = filename.replace(u'Tải nhạc ', '')

    start_time = time.time()
    logging.info("start: %s", filename)
    size = 0
    href = ""
    all_hrefs = list(down_soup.find_all('a'))
    for link in all_hrefs:
        href = link.get('href')
        if href \
                and href.find('downloads') > 0 \
                and href.find(quality) > 0:
            splits_dot = href.split(".")
            org_ext = splits_dot[-1] if len(splits_dot) > 1 else 'mp3'
            filename = filename + f'.{org_ext}'

            write_path = Path(album_path) / filename
            if write_path.exists():
                logging.warn("file %s exists. overwrite.", filename)

            with write_path.open('wb') as f:
                content = ss.get(href).content
                size = f.write(content)
            break
    else:
        logging.error("cannot get href for url=%s", url)
        return

    logging.info("done : %s:: took=%fs, href=%s, bytes=%d", filename, (time.time() - start_time), href, size)


def main(args: argparse.Namespace):
    session = requests.Session()
    # login
    res_init = session.get("https://chiasenhac.vn/",
                           headers={
                               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:82.0) Gecko/20100101 Firefox/82.0',
                           })
    text = res_init.text
    soup = BeautifulSoup(text, 'html.parser')

    x_csrf_token = soup.select('meta[name="csrf-token"]')[0].get('content')

    res_login = session.post(
        "https://chiasenhac.vn/login",
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:82.0) Gecko/20100101 Firefox/82.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://chiasenhac.vn/',
            'Origin': 'https://chiasenhac.vn',
            'DNT': '1',
            'Host': 'chiasenhac.vn',
            'X-CSRF-TOKEN': x_csrf_token
        },
        data={
            "email": args.username,
            "password": args.password,
            "remember": "true"
        })
    if res_login.ok \
            and res_login.status_code == 200 \
            and res_login.json().get('success'):
        logging.info('login ok')
    else:
        logging.error('login not ok')
        logging.error(res_login.text)
        return

    org_page = session.get(args.url).text
    org_soup = BeautifulSoup(org_page, 'html.parser')

    list_url = set()  # link might appear twice, so use set
    d_table = org_soup.find('div', class_='d-table')
    for cell in d_table.select('div.name.d-table-cell'):
        a_tag = cell.find('a')
        if a_tag:
            list_url.add(a_tag.get('href'))
    logging.info('songs: %d', len(list_url))

    # meta
    # artist, album, year
    artist = org_soup.find_all(text="Ca sĩ: ")[0].parent.parent.find('a').text
    album = org_soup.find_all(text="Album: ")[0].parent.parent.find('a').text

    album_path = Path(args.output_dir) / artist / album
    if not album_path.exists():
        album_path.mkdir(parents=True)

    params = [
        (session, url, str(album_path), args.quality)
        for url in list_url
    ]

    p = ThreadPoolExecutor(max_workers=args.num_threads)
    p.map(download_file, params)


if __name__ == '__main__':
    #
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )

    current_dir = Path(__file__).parent
    parser = argparse.ArgumentParser(description='download album from chiasenhac.vn')
    parser.add_argument('--url', '-u', dest='url', type=str, required=True,
                        help='url of the album')
    parser.add_argument('--username', '-U', dest='username', type=str,
                        help='username to login', default=os.getenv('CSN_USERNAME', None))
    parser.add_argument('--password', '-p', dest='password', type=str,
                        help='password to login', default=os.getenv('CSN_PASSWORD', None))
    parser.add_argument('--quality', '-q', dest='quality', type=str, default='320',
                        help='music quality, 128/320/m4a/flac')
    parser.add_argument('--threads', '-t', dest='num_threads', type=int, default=8,
                        help='number of threads')
    parser.add_argument('--output', '-o', dest='output_dir', type=str, default=str(current_dir / 'albums'),
                        help='output folder')

    args: argparse.Namespace = parser.parse_args()
    main(args)
