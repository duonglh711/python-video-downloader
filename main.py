from pytube import YouTube

def youtube_downloader(url, download_location = 'downloads/youtube'):
    YouTube(url).streams \
    .filter(progressive=True, file_extension='mp4') \
    .order_by('resolution') \
    .desc() \
    .first() \
    .download(download_location)

youtube_downloader("https://www.youtube.com/watch?v=4TOEkx2Z1rI")
