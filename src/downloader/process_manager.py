import multiprocessing
from multiprocessing import Process, Pipe
from typing import Optional
from .utils import progress_data, download_media
from .errors import pick_friendly_error

_process_registry: dict = {}
_error_messages: dict = {}

def register_progress(key: str, value: int):
    progress_data[key] = value

def clear_progress(key: str):
    progress_data.pop(key, None)

def get_progress(key: str, default: int = 0) -> int:
    return progress_data.get(key, default)

def get_error_message(key: str) -> Optional[str]:
    return _error_messages.pop(key, None)

def _worker_entry(conn, url, key, download_type, resolution, audio_format, video_format, mode, archive_log):
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
            if conn:
                conn.send({'key': key, 'progress': 100})
        except Exception:
            pass
    except Exception:
        friendly = pick_friendly_error()
        try:
            if conn:
                conn.send({'key': key, 'progress': None, 'error': friendly})
        except Exception:
            pass
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

def start_download(url: str, key: str, download_type: str, resolution: str, audio_format: str, video_format: str, mode: str, archive_log: str | None):
    parent_conn, child_conn = Pipe()
    p = Process(target=_worker_entry, args=(child_conn, url, key, download_type, resolution, audio_format, video_format, mode, archive_log))
    p.start()
    _process_registry[key] = {'process': p, 'conn': parent_conn}
    progress_data[key] = 0

def _poll_ipc():
    remove_keys = []
    for k, v in list(_process_registry.items()):
        conn = v.get('conn')
        proc = v.get('process')
        try:
            if conn:
                while conn.poll():
                    try:
                        msg = conn.recv()
                    except (EOFError, BrokenPipeError, OSError):
                        msg = None
                    if not isinstance(msg, dict):
                        continue
                    key = msg.get('key')
                    prog = msg.get('progress')
                    err = msg.get('error')
                    if key is not None:
                        progress_data[key] = prog
                    if err is not None:
                        progress_data.pop(key, None)
                        _error_messages[key] = f"Error: {err}"
        except Exception:
            pass
        try:
            if not proc.is_alive():
                try:
                    if conn:
                        conn.close()
                except Exception:
                    pass
                remove_keys.append(k)
        except Exception:
            remove_keys.append(k)
    for k in remove_keys:
        _process_registry.pop(k, None)

def poll_ipc():
    _poll_ipc()

def stop_download(key: str):
    entry = _process_registry.get(key)
    if not entry:
        return False, 'No active download for that key'
    proc = entry.get('process')
    conn = entry.get('conn')
    try:
        if proc and proc.is_alive():
            proc.terminate()
    except Exception:
        pass
    try:
        if conn:
            conn.close()
    except Exception:
        pass
    _process_registry.pop(key, None)
    progress_data.pop(key, None)
    _error_messages[key] = "Download cancelled by user!"
    return True, 'Cancelled'
