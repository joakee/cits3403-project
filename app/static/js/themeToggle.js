(function () {
    const STORAGE_KEY = 'theme-preference';
    const DARK_CLASS = 'dark-mode';

    function getSavedTheme() {
        return localStorage.getItem(STORAGE_KEY);
    }

    function getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    function applyTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.classList.add(DARK_CLASS);
        } else {
            document.documentElement.classList.remove(DARK_CLASS);
        }
    }

    function saveTheme(theme) {
        localStorage.setItem(STORAGE_KEY, theme);
    }

    function updateToggleIcon(theme) {
        var btn = document.getElementById('theme-toggle');
        if (!btn) return;
        var icon = btn.querySelector('i');
        if (!icon) return;

        if (theme === 'dark') {
            icon.className = 'bi bi-moon-fill';
            btn.title = 'Switch to light mode';
        } else {
            icon.className = 'bi bi-sun-fill';
            btn.title = 'Switch to dark mode';
        }
    }

    // Apply theme immediately to prevent flash
    var theme = getSavedTheme() || getSystemTheme();
    applyTheme(theme);

    // Wire up toggle button after DOM is ready
    function init() {
        var btn = document.getElementById('theme-toggle');
        if (!btn) return;

        var currentTheme = document.documentElement.classList.contains(DARK_CLASS) ? 'dark' : 'light';
        updateToggleIcon(currentTheme);

        btn.addEventListener('click', function () {
            var isDark = document.documentElement.classList.contains(DARK_CLASS);
            var newTheme = isDark ? 'light' : 'dark';
            applyTheme(newTheme);
            saveTheme(newTheme);
            updateToggleIcon(newTheme);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
