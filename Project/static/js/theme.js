/**
 * WeatherSphere — Theme System
 *
 * The actual theme is applied BEFORE this script runs, by the inline IIFE
 * in base.html <head> that reads localStorage and sets data-bs-theme on
 * <html> immediately. This script's only jobs are:
 *
 *   1. Sync the toggle button icon to whatever theme is already active.
 *   2. Handle toggle button clicks (flip the theme + persist to localStorage).
 *   3. Notify Chart.js to re-render with the new colour palette.
 *
 * There is NO applyTheme() call on page load here — doing so would race
 * with the inline script and could cause a redundant repaint or FOUC.
 */

(function () {
  /**
   * Set the toggle button icon to match the current active theme.
   * Safe to call before DOMContentLoaded because it guards the element lookup.
   */
  function syncIcon(theme) {
    var icon = document.getElementById('themeIcon');
    if (!icon) return;
    if (theme === 'dark') {
      icon.className = 'fa-solid fa-sun text-warning';
    } else {
      icon.className = 'fa-solid fa-moon text-primary';
    }
  }

  /**
   * Apply a theme: update the attribute, persist the choice, sync icon,
   * and notify any dependent modules (charts).
   */
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('weathersphere_theme', theme);
    syncIcon(theme);

    // Let Chart.js re-render with the correct colour palette
    if (window.updateChartColors) {
      window.updateChartColors();
    }
  }

  // Sync the icon as soon as the element is available (DOMContentLoaded).
  document.addEventListener('DOMContentLoaded', function () {
    // The theme attribute is already set on <html> by the inline head script.
    // Just sync the icon and wire the button.
    var currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'dark';
    syncIcon(currentTheme);

    var btn = document.getElementById('themeToggleBtn');
    if (btn) {
      btn.addEventListener('click', function () {
        var active = document.documentElement.getAttribute('data-bs-theme') || 'dark';
        applyTheme(active === 'dark' ? 'light' : 'dark');
      });
    }
  });
})();
