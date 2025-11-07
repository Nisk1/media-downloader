document.addEventListener('DOMContentLoaded', () => {
    const archiveSelect = document.getElementById('archive_log');
    const deleteBtn = document.getElementById('delete-archive-btn');

    if (!archiveSelect) return;

    async function fetchArchives(selectedFile = null) {
        try {
            const response = await fetch('/archives/list/');
            if (!response.ok) throw new Error('Failed to fetch archives');
            const data = await response.json();

            archiveSelect.querySelectorAll('option.dynamic').forEach(opt => opt.remove());

            data.files.forEach(file => {
                const option = document.createElement('option');
                option.value = file;
                option.textContent = file;
                option.classList.add('dynamic');
                archiveSelect.insertBefore(option, archiveSelect.querySelector('option[value="new_file"]'));
            });

            if (selectedFile) {
                archiveSelect.value = selectedFile;
            }
        } catch (err) {
            console.error('Error fetching archives:', err);
        }
    }

    fetchArchives();

    archiveSelect.addEventListener('change', () => {
        if (archiveSelect.value === 'new_file') {
            let newFileName = prompt('Enter new archive file name:');
            if (!newFileName) {
                archiveSelect.value = 'none';
                return;
            }

            fetch('/archives/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ filename: newFileName })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) fetchArchives(data.filename);
                else {
                    alert(data.message || 'Failed to create file');
                    archiveSelect.value = 'none';
                }
            })
            .catch(err => {
                console.error('Error creating file:', err);
                archiveSelect.value = 'none';
            });
        }
    });

    if (deleteBtn && archiveSelect) {
        deleteBtn.addEventListener('click', () => {
            const selectedFile = archiveSelect.value;
            if (!selectedFile || selectedFile === 'none' || selectedFile === 'new_file') {
                alert('Please select a valid archive log to delete.');
                return;
            }

            if (!confirm(`Are you sure you want to delete "${selectedFile}"?`)) return;

            fetch('/archives/delete/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ filename: selectedFile })
            })
            .then(res => res.json())
            .then(data => {
                alert(data.message || (data.success ? 'File deleted successfully' : 'Failed to delete file'));
                fetchArchives();
                archiveSelect.value = 'none';
            })
            .catch(err => {
                console.error('Error deleting archive:', err);
                alert('Error deleting archive.');
            });
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
