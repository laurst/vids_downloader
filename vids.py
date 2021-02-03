import logging
import os

import toml
import youtube_dl

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
    from systemd.journal import JournalHandler

    journald_handler = JournalHandler(SYSLOG_IDENTIFIER='vids.py')
    journald_handler.setFormatter(logging.Formatter(
        '[%(levelname)s] %(message)s'
    ))
    logger.addHandler(journald_handler)
except:
    pass


C = None


def main():
    load_config()

    channels = C['channels']

    for channel, channel_url in channels.items():
        todos = get_todos(channel, channel_url)
        for todo in todos:
            title = todo.get('title', todo['id'])
            logger.info(f"[{channel}] todo : {todo['id']} : {title}")

            download_video(channel, todo['url'])
            maintain_downloaded(channel, todo['id'])

            logger.info(f"[{channel}] maintained {todo['id']}")


def load_config():
    global C

    current_directory = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(current_directory, "vids.toml")
    with open(config_file) as f:
        C = toml.loads(f.read())


def get_todos(channel, channel_url):
    """
    Returns the dict of each item to download, most recent last
    Limits to 10
    """
    vids_directory = C['settings']['vids_directory']
    cache_file = os.path.join(vids_directory, f'.{channel}')

    if os.path.exists(cache_file):
        with open(cache_file) as f:
            existing = set(f.read().splitlines())
    else:
        existing = set()

    playlist_items = get_playlist_items(channel_url)

    todos = []

    for item in playlist_items:
        if 'id' not in item:
            logger.error(f"{item} has no 'id' key")
            break
        if item['id'] in existing:
            break
        todos.append(item)
    todos.reverse()

    logger.info(f"[{channel}] {len(playlist_items)} in channel, "
                f"{len(existing)} existing, {len(todos)} todos")

    return todos[:10]


def maintain_downloaded(channel, todo):
    vids_directory = C['settings']['vids_directory']
    cache_file = os.path.join(vids_directory, f'.{channel}')

    with open(cache_file, "a") as f:
        f.write(f'{todo}\n')


def get_playlist_items(url):
    """
    Returns the entries of a playlist
    """
    ytdl_opts = {
        'extract_flat': 'in_playlist',
        'dumpjson': True,
        'quiet': True,
    }

    with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
        res = ydl.extract_info(url)

    return res['entries']


def download_video(channel, url):
    vids_directory = C['settings']['vids_directory']
    retries = C['settings']['retries']

    logger.info(f'[{channel}] downloading {url}')
    opts = {
        'format': 'best',
        'quiet': True,
        'outtmpl': os.path.join(vids_directory,
                                f'{channel} - %(title)s.%(ext)s'),
    }

    for _ in range(retries):
        try:
            with youtube_dl.YoutubeDL(opts) as ydl:
                output = ydl.extract_info(url)
                result = ydl.prepare_filename(output)
            break
        except Exception as e:
            logger.warning("failed, retrying")
            continue
    else:
        raise RuntimeError(f"could not download {url} after {retries} attempts")


if __name__ == '__main__':
    main()
