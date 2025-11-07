import os
import re
from datetime import datetime
from django.conf import settings
from yt_dlp import YoutubeDL
from multiprocessing.connection import Connection

DOWNLOAD_DIR = os.path.join(settings.BASE_DIR, '..', 'downloads')
DOWNLOAD_DIR = os.path.abspath(DOWNLOAD_DIR)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

ARCHIVES_DIR = os.path.join(settings.BASE_DIR, '..', 'archives')
ARCHIVES_DIR = os.path.abspath(ARCHIVES_DIR)
os.makedirs(ARCHIVES_DIR, exist_ok=True)

progress_data = {}

def normalize_url(url):
    match = re.match(r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]+)", url)
    if match:
        return match.group(1)
    return url

def download_media(url, key, download_type='both', resolution='best', audio_format='default', video_format='default', mode='none', archive_log=None, ipc_conn: Connection = None):
    total_files = 1
    completed_files = 0
    new_files_to_download = 0

    try:
        with YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                total_files = len([e for e in info['entries'] if e])
    except Exception:
        pass

    def progress_hook(d):
        nonlocal completed_files, total_files, new_files_to_download
        if new_files_to_download == 0:
            new_files_to_download = total_files

        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                video_progress = downloaded / total
                value = int(((completed_files + video_progress) / new_files_to_download) * 100)
            else:
                value = int((completed_files / new_files_to_download) * 100)

            progress_data[key] = value
            if ipc_conn:
                try:
                    ipc_conn.send({'key': key, 'progress': value})
                except Exception:
                    pass

        elif d['status'] == 'finished':
            completed_files += 1
            if download_type == 'both':
                completed_files -= 0.5  # adjust for merged file counting

            value = int((completed_files / new_files_to_download) * 100)
            if completed_files >= new_files_to_download:
                value = 100

            progress_data[key] = value
            if ipc_conn:
                try:
                    ipc_conn.send({'key': key, 'progress': value})
                except Exception:
                    pass

    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'quiet': True,
        'progress_hooks': [progress_hook],
    }

    # <-----------------------------(Later adjust the values)
    if mode == 'archival':
        ydl_opts.update({
            'sleep_interval': 1,
            'max_sleep_interval': 5,
            'ratelimit': 1 * 1024 * 1024, # 1 MB/s
            'sleep_requests': 1,
        })

    elif mode == 'safest':
        ydl_opts.update({
            'sleep_interval': 1,
            'max_sleep_interval': 3,
            'ratelimit': 3 * 1024 * 1024, # 3 MB/s
            'sleep_requests': 1,
        })

    elif mode == 'balanced':
        ydl_opts.update({
            'sleep_interval': 1,
            'max_sleep_interval': 2,
            'ratelimit': 10 * 1024 * 1024, # 10 MB/s
            'sleep_requests': 1,
        })

    elif mode == 'fastest':
        ydl_opts.update({
            'sleep_interval': 0,
            'max_sleep_interval': 1,
            'ratelimit': 30 * 1024 * 1024, # 30 MB/s
            'sleep_requests': 1,
        })

    if archive_log:
        archive_path = os.path.join(ARCHIVES_DIR, archive_log)
        ydl_opts['download_archive'] = archive_path

    if download_type == 'audio':
        codec = audio_format if audio_format != 'default' else 'mp3'
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': codec,
                'preferredquality': '192',
            }],
        })

    elif download_type == 'video':
        fmt = 'bestvideo' if resolution == 'best' else f'bestvideo[height<={resolution}]'
        ydl_opts['format'] = fmt
        if video_format != 'default':
            ydl_opts['merge_output_format'] = video_format

    elif download_type == 'urls':
        URLS_DIR = os.path.join(DOWNLOAD_DIR, 'urls')
        os.makedirs(URLS_DIR, exist_ok=True)
        filename = os.path.join(
            URLS_DIR,
            f"urls-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        )

        ydl_opts.update({
            'quiet': True,
            'extract_flat': True,
            'skip_download': True,
        })

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            urls = []

            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        u = entry.get('webpage_url') or entry.get('url')
                        if u:
                            urls.append(u)
            elif info.get('webpage_url') or info.get('url'):
                urls.append(info.get('webpage_url') or info.get('url'))

            with open(filename, 'w', encoding='utf-8') as f:
                for u in urls:
                    f.write(u + '\n')
            progress_data[key] = 100

            if ipc_conn:
                try:
                    ipc_conn.send({'key': key, 'progress': 100})
                except Exception:
                    pass
            return filename

    else:
        fmt = 'bestvideo+bestaudio/best' if resolution == 'best' else f'bestvideo[height<={resolution}]+bestaudio/best'
        ydl_opts['format'] = fmt
        if video_format != 'default':
            ydl_opts['merge_output_format'] = video_format

    if archive_log:
        with open(archive_path, 'r', encoding='utf-8') as f:
            log_urls = [normalize_url(line.strip()) for line in f.readlines()]
        urls_to_download = []

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    video_url = entry.get('webpage_url') or entry.get('url')
                    if video_url and normalize_url(video_url) not in log_urls:
                        urls_to_download.append(video_url)

            new_files_to_download = len(urls_to_download)

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if download_type == 'audio' and audio_format != 'default':
            ext = audio_format
            filename = os.path.splitext(filename)[0] + f'.{ext}'
        return filename
