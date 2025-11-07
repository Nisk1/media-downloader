from multiprocessing import Pipe, Process

try:
    from .utils import download_media
except Exception:
    from utils import download_media

def _entry(
    conn,
    url: str,
    key: str,
    download_type: str,
    resolution: str,
    audio_format: str,
    video_format: str,
    mode: str,
    archive_log: str | None,
):
    try:
        download_media(
            url,
            key=key,
            download_type=download_type,
            resolution=resolution,
            audio_format=audio_format,
            video_format=video_format,
            mode=mode,
            archive_log=archive_log,
            ipc_conn=conn,
        )
        try:
            conn.send({'key': key, 'progress': 100})
        except Exception:
            pass
    except Exception as e:
        try:
            conn.send({'key': key, 'progress': None, 'error': str(e)})
        except Exception:
            pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

def run(
    url: str,
    key: str,
    download_type: str,
    resolution: str,
    audio_format: str,
    video_format: str,
    mode: str,
    archive_log: str | None,
):
    parent_conn, child_conn = Pipe()
    p = Process(
        target=_entry,
        args=(child_conn, url, key, download_type, resolution, audio_format, video_format, mode, archive_log),
    )
    p.daemon = False
    p.start()
    return parent_conn, p
