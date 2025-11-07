import re
import os
import json
import random
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .utils import progress_data, download_media, ARCHIVES_DIR
from .process_manager import start_download, poll_ipc, stop_download, get_progress, register_progress
from .errors import pick_friendly_error
from .archive_manager import list_archives as am_list_archives, create_archive as am_create_archive, delete_archive as am_delete_archive

_DEFAULTS = {
    'selected_download_type': 'both',
    'selected_resolution': 'best',
    'selected_audio_format': 'default',
    'selected_video_format': 'default',
    'message': None,
}

def home(request):
    context = dict(_DEFAULTS)
    if request.method == 'POST':
        url = request.POST.get('url')
        download_type = request.POST.get('download_type')
        resolution = request.POST.get('resolution')
        audio_format = request.POST.get('audio_format', 'default')
        video_format = request.POST.get('video_format', 'default')
        mode = request.POST.get('mode', 'none')
        archive_log = request.POST.get('archive_log')
        if archive_log == 'none':
            archive_log = None
        key = url
        register_progress(key, 0)
        start_download(url, key, download_type, resolution, audio_format, video_format, mode, archive_log)

        return JsonResponse({'started': True})
    return render(request, 'index.html', context)

def download_progress(request):
    poll_ipc()
    key = request.GET.get('key')
    if not key:
        return JsonResponse({'progress': 0})
    progress = get_progress(key, 0)
    message = None

    from .process_manager import get_error_message
    err = get_error_message(key)
    if err is not None:
        message = err
        return JsonResponse({'progress': None, 'message': message})

    if progress == 100:
        message = "Download Complete"
        from .process_manager import clear_progress
        clear_progress(key)

    return JsonResponse({'progress': progress, 'message': message})

def list_archives(request):
    files, err = am_list_archives()
    if err:
        return JsonResponse({'files': [], 'error': err})
    return JsonResponse({'files': files})

@csrf_exempt
def create_archive(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'})

    filename = data.get('filename', '')
    success, result = am_create_archive(filename)

    if success:
        return JsonResponse({'success': True, 'filename': result})
    return JsonResponse({'success': False, 'message': result})

@csrf_exempt
def delete_archive(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'})

    filename = data.get('filename')
    success, result = am_delete_archive(filename)

    if success:
        return JsonResponse({'success': True, 'message': result})
    return JsonResponse({'success': False, 'message': result})

@csrf_exempt
@require_POST
def stop_download_view(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'})

    key = data.get('key')
    if not key:
        return JsonResponse({'success': False, 'message': 'Missing key'})

    success, message = stop_download(key)
    return JsonResponse({'success': success, 'message': message})
