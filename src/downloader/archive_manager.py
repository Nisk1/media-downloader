import os
import re
from django.conf import settings
from .utils import ARCHIVES_DIR

def list_archives():
    try:
        files = [f for f in os.listdir(ARCHIVES_DIR) if f.endswith('.log')]
        return files, None
    except Exception as e:
        return [], str(e)

def _sanitize_filename(filename):
    if not isinstance(filename, str):
        return ''
    name = re.sub(r'[\\/:"*?<>|.;]+', '', filename.strip())
    name = name.replace(' ', '_')
    return name

def create_archive(filename):
    name = _sanitize_filename(filename)
    if not name:
        return False, 'Invalid filename'
    if not name.lower().endswith('.log'):
        name = name + '.log'

    path = os.path.join(ARCHIVES_DIR, name)
    if os.path.exists(path):
        return False, 'File already exists'

    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write('')
        return True, name
    except Exception as e:
        return False, str(e)


def delete_archive(filename):
    if (not filename or not isinstance(filename, str) or not filename.endswith('.log')):
        return False, 'Invalid filename'

    path = os.path.join(ARCHIVES_DIR, filename)
    if not os.path.exists(path):
        return False, 'File not found'

    try:
        os.remove(path)
        return True, f'{filename} deleted successfully'
    except Exception as e:
        return False, str(e)
