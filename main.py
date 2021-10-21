from pytube import YouTube
import requests
from parse_m3u8 import parse_m3u8_file
from file_downloader import ts_download
import os


def youtube_downloader(url, download_location = 'downloads/youtube'):
    YouTube(url).streams \
    .filter(progressive=True, file_extension='mp4') \
    .order_by('resolution') \
    .desc() \
    .first() \
    .download(download_location)


def m3u8_downloader(m3u8_url, file_name = None, download_location = 'downloads/m3u8', n_job = 100):
    os.makedirs(download_location, exist_ok = True)
    download_location = os.path.join(os.getcwd(), download_location)
    if file_name is None:
        file_name = "video"
    ext = ".mp4"

    k = 0
    file_name_temp = file_name
    while os.path.isfile(os.path.join(download_location, file_name + ".mp4")):
        k+=1
        file_name = file_name_temp + str(k)

    prefix_path, url = parse_m3u8_file(m3u8_url)
    ts_download(prefix_path, url, file_name, download_location, n_job)


if __name__ == "__main__":
    # youtube_downloader("https://www.youtube.com/watch?v=4TOEkx2Z1rI")
    m3u8_downloader("https://vnw-vod-cdn.popsww.com/hn-eNRW7KeIO82M-LRK04anLJKPAvw/videos/transcoded/s19_onepiece_800_app-popsapp/index-f3-v1-a1.m3u8"
                , "test")