document.addEventListener('DOMContentLoaded', () => {
    const switcher = document.getElementById('theme-switch');
    if (!switcher) return;

    const storedTheme = localStorage.getItem('theme');

    if (storedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        switcher.checked = true;
    } else if (storedTheme === 'light') {
        document.body.classList.remove('dark-mode');
        switcher.checked = false;
    } else {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (prefersDark) {
            document.body.classList.add('dark-mode');
            switcher.checked = true;
        }
    }

    switcher.addEventListener('change', () => {
        if (switcher.checked) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
        }
    });
});
